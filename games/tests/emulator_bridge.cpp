// Test adapter to the native JR-100 core; test fixtures are explicit.
#include "core_internal.hpp"
#include <algorithm>
#include <cstdint>
using jr100::detail::Emulator;
struct Machine {
    Emulator emulator;
    int low_sp = 0xffff;
    void (*recorder)(void*) = nullptr;
    void* recorder_context = nullptr;
    long long next_frame = 0;
    unsigned mutations = 0;
    Machine(const uint8_t* rom, int length) : emulator({rom, size_t(length)}, false) {}
    void step() {
        emulator.cpu().step_instruction();
        emulator.via().execute(emulator.clock_count());
        const auto& r = emulator.cpu().registers();
        if (r.pc >= 0x300 && r.pc < 0x3000) low_sp = std::min(low_sp, int(r.sp));
        if (recorder && emulator.clock_count() >= next_frame) {
            next_frame += 14900;
            recorder(recorder_context);
        }
    }
};
extern "C" {
Machine* create(const uint8_t* rom, int length) { return new Machine(rom, length); }
void destroy(Machine* m) { delete m; }
int peek(Machine* m, int address) { return m->emulator.load8(address); }
void poke(Machine* m, int address, int value) { ++m->mutations; m->emulator.store8(address, value); }
void fixture_pc(Machine* m, int pc, int sp) {
    ++m->mutations;
    auto& r = const_cast<jr100::detail::CpuRegisters&>(m->emulator.cpu().registers());
    r.pc = pc; r.sp = sp;
    const_cast<jr100::detail::CpuFlags&>(m->emulator.cpu().flags()).i = true;
}
int pc(Machine* m) { return m->emulator.cpu().registers().pc; }
void reset_stats(Machine* m) { m->low_sp = 0xffff; }
int min_sp(Machine* m) { return m->low_sp; }
long long clocks(Machine* m) { return m->emulator.clock_count(); }
int until(Machine* m, int address, int budget) {
    const auto end = m->emulator.clock_count() + budget;
    do {
        m->step();
        if (m->emulator.cpu().registers().pc == address) return 1;
    } while (m->emulator.clock_count() < end);
    return 0;
}
int until_either(Machine* m, int first, int second, int budget) {
    const auto end = m->emulator.clock_count() + budget;
    do {
        m->step();
        const auto address = m->emulator.cpu().registers().pc;
        if (address == first) return 1;
        if (address == second) return 2;
    } while (m->emulator.clock_count() < end);
    return 0;
}
void ticks(Machine* m, int cycles) {
    auto end = m->emulator.clock_count() + cycles;
    while(m->emulator.clock_count() < end) m->step();
}
void frame(Machine* m) {
    if (m->recorder) ticks(m, 14900);
    else m->emulator.run_frame(14900);
}
void record_frames(Machine* m, void (*callback)(void*), void* context) {
    m->recorder = callback;
    m->recorder_context = context;
    m->next_frame = m->emulator.clock_count() + 14900;
}
unsigned host_mutations(Machine* m) { return m->mutations; }
int load_prg(Machine* m, const uint8_t* data, int length) {
    try { m->emulator.load_program({data, size_t(length)}, "game.prg"); return 1; }
    catch (...) { return 0; }
}
void key(Machine* m, int row, int bit, int pressed) { m->emulator.set_key(row, bit, pressed); }
void pad(Machine* m, int mask) { m->emulator.set_joystick_mask(mask); }
void pixels(Machine* m, uint8_t* output) {
    const auto data = m->emulator.frame_buffer();
    std::copy(data.begin(), data.end(), output);
}
int audio_peak(Machine* m) {
    auto& s = m->emulator.sound();
    s.execute(m->emulator.clock_count());
    int peak = 0;
    for(auto value : s.samples()) peak = std::max(peak, std::abs(int(value)));
    s.clear_samples();
    return peak;
}
int audio_size(Machine* m) {
    auto& sound = m->emulator.sound();
    sound.execute(m->emulator.clock_count());
    return int(sound.samples().size());
}
void audio_copy(Machine* m, int16_t* output) {
    auto& sound = m->emulator.sound();
    std::copy(sound.samples().begin(), sound.samples().end(), output);
    sound.clear_samples();
}
}
