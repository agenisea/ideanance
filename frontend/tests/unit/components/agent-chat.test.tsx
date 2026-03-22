import { render, screen, fireEvent } from "@testing-library/react";
import { AgentChat } from "@/components/agents/agent-chat";
import { useSSEStream } from "@agenisea/sse-kit/client";

vi.mock("@agenisea/sse-kit/client", () => ({
  useSSEStream: vi.fn(() => ({
    state: { event: "idle", isStreaming: false, data: null, error: null },
    start: vi.fn(),
    cancel: vi.fn(),
    reset: vi.fn(),
  })),
}));

describe("AgentChat", () => {
  it("renders agent selector buttons", () => {
    render(<AgentChat projectId="p1" workspaceId="w1" />);
    expect(screen.getByText("design advisor")).toBeInTheDocument();
    expect(screen.getByText("policy interpreter")).toBeInTheDocument();
  });

  it("renders input and send button", () => {
    render(<AgentChat projectId="p1" workspaceId="w1" />);
    expect(
      screen.getByPlaceholderText("Ask about governance...")
    ).toBeInTheDocument();
    expect(screen.getByText("Send")).toBeInTheDocument();
  });

  it("send button is disabled when input is empty", () => {
    render(<AgentChat projectId="p1" workspaceId="w1" />);
    expect(screen.getByText("Send")).toBeDisabled();
  });

  it("send button enables when input has text", () => {
    render(<AgentChat projectId="p1" workspaceId="w1" />);
    fireEvent.change(screen.getByPlaceholderText("Ask about governance..."), {
      target: { value: "What is GOVERN-1.1?" },
    });
    expect(screen.getByText("Send")).not.toBeDisabled();
  });

  it("shows streaming indicator with aria-live when streaming", () => {
    vi.mocked(useSSEStream).mockReturnValue({
      state: { event: "token", isStreaming: true, data: null, error: null },
      start: vi.fn(),
      cancel: vi.fn(),
      reset: vi.fn(),
    } as ReturnType<typeof useSSEStream>);

    render(<AgentChat projectId="p1" workspaceId="w1" />);
    const liveRegion = screen.getByText("Thinking...");
    expect(liveRegion).toBeInTheDocument();
    expect(liveRegion).toHaveAttribute("aria-live", "polite");
  });

  it("disables input while streaming", () => {
    vi.mocked(useSSEStream).mockReturnValue({
      state: { event: "token", isStreaming: true, data: null, error: null },
      start: vi.fn(),
      cancel: vi.fn(),
      reset: vi.fn(),
    } as ReturnType<typeof useSSEStream>);

    render(<AgentChat projectId="p1" workspaceId="w1" />);
    expect(
      screen.getByPlaceholderText("Ask about governance...")
    ).toBeDisabled();
  });
});
