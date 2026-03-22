import { useSSEStream } from "@agenisea/sse-kit/client";
import { useAgentStream } from "@/hooks/use-agent-stream";

vi.mock("@agenisea/sse-kit/client", () => ({
  useSSEStream: vi.fn(() => ({
    state: { event: "idle", isStreaming: false, data: null, error: null },
    start: vi.fn(),
    cancel: vi.fn(),
    reset: vi.fn(),
  })),
}));

describe("useAgentStream", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calls useSSEStream with correct endpoint for agent", () => {
    // Direct function call since it's a thin wrapper
    useAgentStream("design_advisor");
    expect(useSSEStream).toHaveBeenCalledWith(
      expect.objectContaining({
        endpoint: "/api/v1/agents/design_advisor/run",
        method: "POST",
        initialEvent: "idle",
        completeEvent: "done",
        errorEvent: "error",
      })
    );
  });

  it("configures POST method with JSON content type", () => {
    useAgentStream("policy_interpreter");
    expect(useSSEStream).toHaveBeenCalledWith(
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
      })
    );
  });

  it("returns start, cancel, and reset functions", () => {
    const result = useAgentStream("design_advisor");
    expect(typeof result.start).toBe("function");
    expect(typeof result.cancel).toBe("function");
    expect(typeof result.reset).toBe("function");
  });

  it("returns idle state initially", () => {
    const result = useAgentStream("design_advisor");
    expect(result.state.event).toBe("idle");
    expect(result.state.isStreaming).toBe(false);
  });
});
