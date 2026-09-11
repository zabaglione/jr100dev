// Test-only bridge to the current JR100 emulator. No emulator source changes.
#include "core_internal.hpp"
#include <algorithm>
#include <cstdint>
#include <cstring>
using jr100::detail::Emulator;
static uint16_t low_sp = 0xffff;
static int stream_begin = -1, stream_end = -1, stream_base = 0;
static int stream_low_sp = 0xffff, stream_errors = 0;
static int skip_render_pc = -1;
static int game_mode_address = 0;
static uint64_t mutation_count = 0;
static bool watch_video = false;
static int video_store_a, video_store_b;
static uint64_t video_writes, video_redundant, video_outside, video_repeated;
static uint64_t video_first, video_last;
static unsigned video_touches[768];
static void trace_video(Emulator* e) {
    if (!watch_video) return;
    const auto& r = e->cpu().registers();
    int op = e->load8(r.pc), address = -1;
    if (op == 0xa7 || op == 0xe7) address = (r.ix + e->load8(r.pc + 1)) & 0xffff;
    if (op == 0xb7 || op == 0xf7) address = e->load16(r.pc + 1);
    if (address < 0xc100 || address >= 0xc400) return;
    int value = (op == 0xa7 || op == 0xb7) ? r.a : r.b;
    if (!video_writes) video_first = e->clock_count();
    video_last = e->clock_count();
    ++video_writes;
    video_redundant += e->load8(address) == value;
    video_outside += r.pc != video_store_a && r.pc != video_store_b;
    video_repeated += video_touches[address - 0xc100]++ != 0;
}
extern "C" {
void stack_stream_range(int begin, int end, int base) {
    stream_begin = begin; stream_end = end; stream_base = base;
}
int stack_stream_stat(int id) { return id == 0 ? stream_low_sp : stream_errors; }
void video_watch(int a, int b) {
    watch_video = true; video_store_a = a; video_store_b = b;
    video_writes = video_redundant = video_outside = video_repeated = 0;
    video_first = video_last = 0;
    std::fill(std::begin(video_touches), std::end(video_touches), 0);
}
long long video_stat(int id) {
    switch(id) {
    case 0: return video_writes; case 1: return video_redundant;
    case 2: return video_outside; case 3: return video_repeated;
    default: return video_last - video_first;
    }
}
void video_watch_stop() { watch_video = false; }

Emulator* create(const uint8_t* rom, int size) {
    auto* e = new Emulator({rom, static_cast<size_t>(size)}, false);
    e->tick(1);
    return e;
}
void destroy(Emulator* e) { delete e; }
void poke(Emulator* e, int address, int value) { ++mutation_count; e->store8(address,value); }
int peek(Emulator* e, int address) { return e->load8(address); }
void read_bytes(Emulator* e, int address, uint8_t* out, int size) {
    for(int i=0;i<size;i++) out[i]=e->load8(address+i);
}
void registers_set(Emulator* e,int pc,int sp,int a,int b,int ix) {
    ++mutation_count;
    auto& r=const_cast<jr100::detail::CpuRegisters&>(e->cpu().registers());
    r.pc=pc;r.sp=sp;r.a=a;r.b=b;r.ix=ix;
    auto& f=const_cast<jr100::detail::CpuFlags&>(e->cpu().flags());
    f.i=true;
}
int reg(Emulator* e,int id) {
    auto& r=e->cpu().registers();
    switch(id){case 0:return r.pc;case 1:return r.sp;case 2:return r.a;case 3:return r.b;default:return r.ix;}
}
long long clocks(Emulator* e) { return e->clock_count(); }
int audio_peak(Emulator* e) {
    auto& sound = e->sound();
    sound.execute(e->clock_count());
    int peak = 0;
    for (auto sample : sound.samples()) peak = std::max(peak, std::abs(int(sample)));
    sound.clear_samples();
    return peak;
}
int run_until(Emulator* e, int pc, int max_cycles) {
    auto end=e->clock_count()+max_cycles;
    do {
        if(e->cpu().registers().pc==skip_render_pc && e->load8(game_mode_address)==1) {
            auto& r=const_cast<jr100::detail::CpuRegisters&>(e->cpu().registers());
            r.pc=e->load16(r.sp+1);r.sp+=2;
            e->set_clock_count(e->clock_count()+5);
        } else { trace_video(e); e->cpu().step_instruction(); }
        e->via().execute(e->clock_count());
        const auto& r = e->cpu().registers();
        if (r.pc >= stream_begin && r.pc <= stream_end) {
            stream_low_sp = std::min(stream_low_sp, int(r.sp));
            stream_errors += r.sp < stream_base - 1 || r.sp >= stream_base + 768 || !e->cpu().flags().i;
        } else low_sp = std::min(low_sp, r.sp);
        if(e->cpu().registers().pc==pc)return 1;
    } while(e->clock_count()<end);
    return 0;
}
void key(Emulator* e,int row,int bit,int down) {e->set_key(row,bit,down);}
void pad(Emulator* e,int bits) {e->set_joystick_mask(bits);}
void pixels(Emulator* e,uint8_t* out) { auto f=e->frame_buffer();std::copy(f.begin(),f.end(),out); }
void headless_search(int render_pc,int mode_address){skip_render_pc=render_pc;game_mode_address=mode_address;}
int min_sp(){return low_sp;}
void reset_min_sp(){low_sp=0xffff;stream_low_sp=0xffff;stream_errors=0;}
}
// Planning checkpoints are used only in disposable search machines.
// The acceptance replay uses create/key/pad/run_until and never restore.
struct Snapshot {
    std::array<uint8_t, 0x4000> ram;
    std::array<uint8_t, 0x400> video;
    jr100::detail::ViaRegisters via;
    jr100::detail::CpuRegisters registers;
    jr100::detail::CpuFlags flags;
    int64_t clock;
};
extern "C" {
Snapshot* snapshot(Emulator* e) {
    auto* s=new Snapshot;
    for(int i=0;i<0x4000;i++)s->ram[i]=e->load8(i);
    for(int i=0;i<0x400;i++)s->video[i]=e->load8(0xc000+i);
    s->via=e->via().registers();
    s->registers=e->cpu().registers();s->flags=e->cpu().flags();s->clock=e->clock_count();
    return s;
}
void restore(Emulator* e, Snapshot* s) {
    ++mutation_count;
    for(int i=0;i<0x4000;i++)e->store8(i,s->ram[i]);
    for(int i=0;i<0x400;i++)e->store8(0xc000+i,s->video[i]);
    const_cast<jr100::detail::ViaRegisters&>(e->via().registers())=s->via;
    e->set_font_plane((s->via.orb & s->via.ddrb & 0x20)!=0);
    e->cpu().set_irq_line((s->via.ier & s->via.ifr & 0x7f)!=0);
    e->clear_keys();e->set_joystick_mask(0);
    const_cast<jr100::detail::CpuRegisters&>(e->cpu().registers())=s->registers;
    const_cast<jr100::detail::CpuFlags&>(e->cpu().flags())=s->flags;
    e->set_clock_count(s->clock);
}
void snapshot_free(Snapshot* s){delete s;}
}
extern "C" int headless_search_enabled(){return skip_render_pc>=0;}

extern "C" uint64_t mutations(){return mutation_count;}
