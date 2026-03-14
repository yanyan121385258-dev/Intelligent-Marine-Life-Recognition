import { request } from '@/utils/hertz_request';

import type { ApiResponse } from '@/types/api_response';

// 会话与消息类型
export interface AIChatItem {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  latest_message?: string;
}

export interface AIChatDetail {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface AIChatMessage {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface ChatListData {
  total: number;
  page: number;
  page_size: number;
  chats: AIChatItem[];
}

export interface ChatDetailData {
  chat: AIChatDetail;
  messages: AIChatMessage[];
}

export interface SendMessageData {
  user_message: AIChatMessage;
  ai_message: AIChatMessage;
}

// 将后端可能返回的 chat_id 统一规范为 id
const normalizeChatItem = (raw: any): AIChatItem => ({
  id: typeof raw?.id === 'number' ? raw.id : Number(raw?.chat_id),
  title: raw?.title,
  created_at: raw?.created_at,
  updated_at: raw?.updated_at,
  latest_message: raw?.latest_message,
});

const normalizeChatDetail = (raw: any): AIChatDetail => ({
  id: typeof raw?.id === 'number' ? raw.id : Number(raw?.chat_id),
  title: raw?.title,
  created_at: raw?.created_at,
  updated_at: raw?.updated_at,
});

export const aiApi = {
  listChats: (params?: {
    query?: string;
    page?: number;
    page_size?: number;
  }): Promise<ApiResponse<ChatListData>> =>
    request.get('/api/ai/chats/', { params, showError: false }).then((resp: any) => {
      if (resp?.data?.chats && Array.isArray(resp.data.chats)) {
        resp.data.chats = resp.data.chats.map((c: any) => normalizeChatItem(c));
      }
      return resp as ApiResponse<ChatListData>;
    }),

  createChat: (body?: { title?: string }): Promise<ApiResponse<AIChatDetail>> =>
    request.post('/api/ai/chats/create/', body || { title: '新对话' }).then((resp: any) => {
      if (resp?.data) resp.data = normalizeChatDetail(resp.data);
      return resp as ApiResponse<AIChatDetail>;
    }),

  getChatDetail: (chatId: number): Promise<ApiResponse<ChatDetailData>> =>
    request.get(`/api/ai/chats/${chatId}/`).then((resp: any) => {
      if (resp?.data?.chat) resp.data.chat = normalizeChatDetail(resp.data.chat);
      return resp as ApiResponse<ChatDetailData>;
    }),

  updateChat: (chatId: number, body: { title: string }): Promise<ApiResponse<null>> =>
    request.put(`/api/ai/chats/${chatId}/update/`, body),

  deleteChats: (chatIds: number[]): Promise<ApiResponse<null>> =>
    request.post('/api/ai/chats/delete/', { chat_ids: chatIds }),

  sendMessage: (chatId: number, body: { content: string }): Promise<ApiResponse<SendMessageData>> =>
    request.post(`/api/ai/chats/${chatId}/send/`, body),
};
