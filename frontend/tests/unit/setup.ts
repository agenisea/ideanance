import "@testing-library/jest-dom/vitest";

// Mock @agenisea/sse-kit for all tests
vi.mock("@agenisea/sse-kit/client", () => ({
  useSSEStream: vi.fn(() => ({
    state: { event: "idle", isStreaming: false, data: null, error: null },
    start: vi.fn(),
    cancel: vi.fn(),
    reset: vi.fn(),
  })),
}));
