/**
 * 聊天状态管理（Zustand）
 */
import { create } from 'zustand';
import { Session, Message, ChatState } from '../types/chat';
import { generateUUID } from '../utils/validators';

interface ChatStore extends ChatState {
  // Actions
  createSession: () => string;
  setCurrentSession: (sessionId: string) => void;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setMessages: (messages: Message[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  updateSessionTitle: (sessionId: string, title: string) => void;
  deleteSession: (sessionId: string) => void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  // State
  sessions: [],
  currentSessionId: null,
  messages: [],
  isLoading: false,
  error: null,

  // Actions
  createSession: () => {
    const sessionId = generateUUID();
    const newSession: Session = {
      id: sessionId,
      title: '新会话',
      createdAt: Date.now(),
      updatedAt: Date.now(),
      messageCount: 0,
    };

    set((state) => ({
      sessions: [newSession, ...state.sessions],
      currentSessionId: sessionId,
      messages: [],
      error: null,
    }));

    return sessionId;
  },

  setCurrentSession: (sessionId: string) => {
    set({ currentSessionId: sessionId, messages: [], error: null });
  },

  addMessage: (message) => {
    const newMessage: Message = {
      ...message,
      id: generateUUID(),
      timestamp: Date.now(),
    };

    set((state) => ({
      messages: [...state.messages, newMessage],
      error: null,
    }));

    // 更新会话的更新时间
    if (state.currentSessionId) {
      set((state) => ({
        sessions: state.sessions.map((session) =>
          session.id === state.currentSessionId
            ? {
                ...session,
                updatedAt: Date.now(),
                messageCount: session.messageCount + 1,
              }
            : session
        ),
      }));
    }
  },

  setMessages: (messages) => {
    set({ messages });
  },

  setLoading: (isLoading) => {
    set({ isLoading });
  },

  setError: (error) => {
    set({ error });
  },

  updateSessionTitle: (sessionId, title) => {
    set((state) => ({
      sessions: state.sessions.map((session) =>
        session.id === sessionId ? { ...session, title } : session
      ),
    }));
  },

  deleteSession: (sessionId) => {
    set((state) => {
      const newSessions = state.sessions.filter((s) => s.id !== sessionId);
      const newCurrentSessionId =
        state.currentSessionId === sessionId
          ? newSessions[0]?.id || null
          : state.currentSessionId;

      return {
        sessions: newSessions,
        currentSessionId: newCurrentSessionId,
        messages: newCurrentSessionId === sessionId ? [] : state.messages,
      };
    });
  },
}));

