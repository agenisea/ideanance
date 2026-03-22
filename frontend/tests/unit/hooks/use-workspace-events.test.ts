import { useSSEStream } from "@agenisea/sse-kit/client";
import { useWorkspaceEvents } from "@/hooks/use-workspace-events";

vi.mock("@agenisea/sse-kit/client", () => ({
  useSSEStream: vi.fn(() => ({
    state: { event: "idle", isStreaming: false, data: null, error: null },
    start: vi.fn(),
    cancel: vi.fn(),
    reset: vi.fn(),
  })),
}));

describe("useWorkspaceEvents", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calls useSSEStream with GET method for workspace stream", () => {
    useWorkspaceEvents("ws-123");
    expect(useSSEStream).toHaveBeenCalledWith(
      expect.objectContaining({
        endpoint: "/api/v1/events/stream/ws-123",
        method: "GET",
      })
    );
  });

  it("uses __never__ as completeEvent for long-lived stream", () => {
    useWorkspaceEvents("ws-456");
    expect(useSSEStream).toHaveBeenCalledWith(
      expect.objectContaining({
        completeEvent: "__never__",
      })
    );
  });

  it("returns idle state initially", () => {
    const result = useWorkspaceEvents("ws-789");
    expect(result.state.event).toBe("idle");
    expect(result.state.isStreaming).toBe(false);
  });
});
