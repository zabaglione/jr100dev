export function createFrameScheduler({ requestFrame, cancelFrame, task }) {
  if (typeof requestFrame !== "function" || typeof cancelFrame !== "function" || typeof task !== "function") {
    throw new TypeError("Frame scheduler requires request, cancel, and task functions");
  }

  let frameId = null;

  return {
    schedule() {
      if (frameId !== null) return false;
      frameId = requestFrame(() => {
        frameId = null;
        task();
      });
      return true;
    },
    cancel() {
      if (frameId === null) return false;
      cancelFrame(frameId);
      frameId = null;
      return true;
    },
    isPending() {
      return frameId !== null;
    },
  };
}
