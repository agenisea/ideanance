import { create } from "zustand";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  agentId?: string;
}

interface ChatState {
  messages: Record<string, Message[]>;
  addMessage: (projectId: string, message: Message) => void;
  clearChat: (projectId: string) => void;
  getMessages: (projectId: string) => Message[];
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: {},
  addMessage: (projectId, message) =>
    set((state) => ({
      messages: {
        ...state.messages,
        [projectId]: [...(state.messages[projectId] || []), message],
      },
    })),
  clearChat: (projectId) =>
    set((state) => ({
      messages: { ...state.messages, [projectId]: [] },
    })),
  getMessages: (projectId) => get().messages[projectId] || [],
}));

export type { Message };
