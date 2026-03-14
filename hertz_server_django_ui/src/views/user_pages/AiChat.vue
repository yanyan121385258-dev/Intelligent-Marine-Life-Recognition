<template>
  <div class="ai-chat-page">
    <div class="page-header">
      <h1 class="page-title">
        <MessageOutlined class="title-icon" />
        AI助手
      </h1>
      <p class="page-description">智能对话，快速解答您的问题</p>
    </div>

    <!-- 错误提示 -->
    <div class="error-container" v-if="errorInfo && (errorInfo.status ?? 0) >= 400">
      <a-alert
        type="error"
        show-icon
        closable
        @close="errorInfo = null"
        :message="`请求失败：${errorInfo.message || '网络错误'}`"
        class="error-alert"
      >
        <template #description>
          <a-descriptions :column="1" size="small">
            <a-descriptions-item label="状态码">{{
              errorInfo.status ?? '未知'
            }}</a-descriptions-item>
            <a-descriptions-item label="请求方法">{{
              errorInfo.method || 'GET'
            }}</a-descriptions-item>
            <a-descriptions-item label="请求地址">{{ errorInfo.url || '-' }}</a-descriptions-item>
            <a-descriptions-item label="请求数据">
              <pre class="err-pre">{{ formatJson(errorInfo.requestData) }}</pre>
            </a-descriptions-item>
            <a-descriptions-item label="响应数据">
              <pre class="err-pre">{{ formatJson(errorInfo.data) }}</pre>
            </a-descriptions-item>
          </a-descriptions>
        </template>
      </a-alert>
    </div>

    <div class="chat-container">
      <!-- 操作栏 -->
      <div class="action-bar">
        <a-input-search
          ref="searchRef"
          v-model:value="query"
          placeholder="搜索会话标题..."
          class="search-input"
          @search="fetchChats"
          style="max-width: 300px"
        />
        <a-space>
          <a-button @click="fetchChats" :loading="loadingChats">
            <template #icon>
              <ReloadOutlined />
            </template>
            刷新
          </a-button>
          <a-button type="primary" @click="createChat" :loading="creating">
            <template #icon>
              <PlusOutlined />
            </template>
            新建对话
          </a-button>
        </a-space>
      </div>

      <!-- 布局1：标准左右分栏布局 -->
      <template v-if="currentLayout === 'default'">
        <a-row :gutter="[16, 16]">
          <!-- 左侧：会话列表 -->
          <a-col :xs="24" :md="24" :lg="7">
            <div class="chat-sidebar sidebar-standard">
              <div class="sidebar-header">
                <div class="header-icon">
                  <MessageOutlined />
                </div>
                <h3 class="sidebar-title">我的对话</h3>
              </div>
              <div class="chat-list">
                <a-list
                  :data-source="chatList"
                  item-layout="horizontal"
                  :loading="loadingChats"
                  :pagination="{
                    pageSize: pageSize,
                    total: total,
                    current: page,
                    onChange: onPageChange,
                  }"
                >
                  <template #renderItem="{ item }">
                    <a-list-item
                      :class="{ active: item.id === currentChatId }"
                      @click="selectChat(item.id)"
                      class="chat-item"
                    >
                      <a-list-item-meta>
                        <template #title>
                          <div class="chat-title-row">
                            <span class="chat-title">{{ item.title }}</span>
                            <a-space>
                              <a-button
                                size="small"
                                type="text"
                                @click.stop="openRename(item)"
                                class="edit-btn"
                              >
                                <EditOutlined />
                              </a-button>
                              <a-popconfirm title="确认删除该对话？" @confirm="deleteChat(item.id)">
                                <a-button
                                  size="small"
                                  danger
                                  type="text"
                                  @click.stop
                                  class="delete-btn"
                                >
                                  <DeleteOutlined />
                                </a-button>
                              </a-popconfirm>
                            </a-space>
                          </div>
                        </template>
                        <template #description>
                          <div class="chat-desc">{{ item.latest_message || '暂无消息' }}</div>
                        </template>
                      </a-list-item-meta>
                    </a-list-item>
                  </template>
                </a-list>
              </div>
            </div>
          </a-col>
          <!-- 右侧：消息区 -->
          <a-col :xs="24" :md="24" :lg="17">
            <div class="chat-main main-standard">
              <div class="chat-header">
                <div class="header-icon">
                  <RobotOutlined />
                </div>
                <div class="header-content">
                  <h3 class="chat-title">{{ currentChat?.title || '请选择或新建对话' }}</h3>
                  <p class="chat-subtitle">与AI助手开始智能对话</p>
                </div>
              </div>

              <div class="chat-content">
                <div class="messages-wrapper">
                  <div class="messages" ref="messagesEl">
                    <template v-if="messages.length">
                      <div v-for="m in messages" :key="m.id" :class="['msg', m.role]">
                        <div class="message-avatar">
                          <a-avatar
                            :size="32"
                            :style="{ backgroundColor: m.role === 'user' ? '#3b82f6' : '#10b981' }"
                          >
                            <template #icon>
                              <UserOutlined v-if="m.role === 'user'" />
                              <RobotOutlined v-else />
                            </template>
                          </a-avatar>
                        </div>
                        <div class="message-content">
                          <div class="bubble">
                            <div class="content">
                              <div
                                v-if="m.id === loadingMessageId && m.role === 'assistant'"
                                class="typing-indicator"
                              >
                                <div class="typing-circle"></div>
                                <div class="typing-circle"></div>
                                <div class="typing-circle"></div>
                                <div class="typing-shadow"></div>
                                <div class="typing-shadow"></div>
                                <div class="typing-shadow"></div>
                              </div>
                              <div v-else v-html="renderContent(m.content)"></div>
                            </div>
                            <div class="time">{{ formatTime(m.created_at) }}</div>
                          </div>
                        </div>
                      </div>
                    </template>
                    <div v-else class="empty-messages">
                      <a-empty description="暂无消息，开始你的第一次对话吧！">
                        <template #image>
                          <MessageOutlined style="font-size: 64px; color: #d9d9d9" />
                        </template>
                      </a-empty>
                    </div>
                  </div>
                </div>

                <div class="composer" v-if="currentChatId">
                  <div class="input-container">
                    <a-textarea
                      v-model:value="input"
                      :rows="3"
                      placeholder="输入你的问题..."
                      :disabled="!currentChatId"
                      @pressEnter="onEnterSend"
                      @keydown="onComposerKeydown"
                      class="message-input"
                    />
                    <div class="input-actions">
                      <a-button
                        type="primary"
                        :disabled="!canSend"
                        @click="send"
                        class="send-btn"
                        size="large"
                      >
                        <template #icon>
                          <SendOutlined />
                        </template>
                        发送消息
                      </a-button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </a-col>
        </a-row>
      </template>

      <!-- 布局2：上下分割布局 -->
      <template v-else-if="currentLayout === 'compact'">
        <div class="chat-container-vertical">
          <!-- 上侧：会话列表 -->
          <div class="chat-sidebar-vertical sidebar-compact">
            <div class="sidebar-header">
              <div class="header-icon">
                <MessageOutlined />
              </div>
              <h3 class="sidebar-title">我的对话</h3>
            </div>
            <div class="chat-list-horizontal">
              <a-list
                :data-source="chatList"
                item-layout="horizontal"
                :loading="loadingChats"
                :pagination="{
                  pageSize: pageSize,
                  total: total,
                  current: page,
                  onChange: onPageChange,
                }"
                :grid="{ gutter: 16, column: 4 }"
              >
                <template #renderItem="{ item }">
                  <a-list-item
                    :class="{ active: item.id === currentChatId }"
                    @click="selectChat(item.id)"
                    class="chat-item-horizontal"
                  >
                    <a-card
                      :class="{ 'active-card': item.id === currentChatId }"
                      size="small"
                      hoverable
                    >
                      <div class="horizontal-chat-title">{{ item.title }}</div>
                      <div class="horizontal-chat-desc">
                        {{ item.latest_message || '暂无消息' }}
                      </div>
                    </a-card>
                  </a-list-item>
                </template>
              </a-list>
            </div>
          </div>
          <!-- 下侧：消息区 -->
          <div class="chat-main-vertical main-compact">
            <div class="chat-header">
              <div class="header-icon">
                <RobotOutlined />
              </div>
              <div class="header-content">
                <h3 class="chat-title">{{ currentChat?.title || '请选择或新建对话' }}</h3>
                <p class="chat-subtitle">与AI助手开始智能对话</p>
              </div>
            </div>

            <div class="chat-content">
              <div class="messages-wrapper">
                <div class="messages" ref="messagesEl">
                  <template v-if="messages.length">
                    <div v-for="m in messages" :key="m.id" :class="['msg', m.role]">
                      <div class="message-avatar">
                        <a-avatar
                          :size="32"
                          :style="{ backgroundColor: m.role === 'user' ? '#3b82f6' : '#10b981' }"
                        >
                          <template #icon>
                            <UserOutlined v-if="m.role === 'user'" />
                            <RobotOutlined v-else />
                          </template>
                        </a-avatar>
                      </div>
                      <div class="message-content">
                        <div class="bubble">
                          <div class="content">
                            <div
                              v-if="m.id === loadingMessageId && m.role === 'assistant'"
                              class="typing-indicator"
                            >
                              <div class="typing-circle"></div>
                              <div class="typing-circle"></div>
                              <div class="typing-circle"></div>
                              <div class="typing-shadow"></div>
                              <div class="typing-shadow"></div>
                              <div class="typing-shadow"></div>
                            </div>
                            <div v-else v-html="renderContent(m.content)"></div>
                          </div>
                          <div class="time">{{ formatTime(m.created_at) }}</div>
                        </div>
                      </div>
                    </div>
                  </template>
                  <div v-else class="empty-messages">
                    <a-empty description="暂无消息，开始你的第一次对话吧！">
                      <template #image>
                        <MessageOutlined style="font-size: 64px; color: #d9d9d9" />
                      </template>
                    </a-empty>
                  </div>
                </div>
              </div>

              <div class="composer" v-if="currentChatId">
                <div class="input-container">
                  <a-textarea
                    v-model:value="input"
                    :rows="3"
                    placeholder="输入你的问题..."
                    :disabled="!currentChatId"
                    @pressEnter="onEnterSend"
                    class="message-input"
                  />
                  <div class="input-actions">
                    <a-button
                      type="primary"
                      :disabled="!canSend"
                      @click="send"
                      class="send-btn"
                      size="large"
                    >
                      <template #icon>
                        <SendOutlined />
                      </template>
                      发送消息
                    </a-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- 布局3：全屏消息区 + 悬浮侧边栏 -->
      <template v-else-if="currentLayout === 'wide'">
        <div class="chat-container-wide">
          <!-- 悬浮侧边栏按钮 -->
          <a-button
            type="primary"
            shape="circle"
            class="sidebar-toggle-btn"
            @click="sidebarVisible = !sidebarVisible"
          >
            <template #icon>
              <MessageOutlined />
            </template>
          </a-button>

          <!-- 可折叠侧边栏 -->
          <div class="chat-sidebar-floating" :class="{ visible: sidebarVisible }">
            <div class="sidebar-header">
              <div class="header-icon">
                <MessageOutlined />
              </div>
              <h3 class="sidebar-title">我的对话</h3>
              <a-button
                type="text"
                shape="circle"
                class="close-sidebar"
                @click="sidebarVisible = false"
              >
                <template #icon>
                  <CloseOutlined />
                </template>
              </a-button>
            </div>
            <div class="chat-list">
              <a-list
                :data-source="chatList"
                item-layout="horizontal"
                :loading="loadingChats"
                :pagination="{
                  pageSize: pageSize,
                  total: total,
                  current: page,
                  onChange: onPageChange,
                }"
              >
                <template #renderItem="{ item }">
                  <a-list-item
                    :class="{ active: item.id === currentChatId }"
                    @click="selectChat(item.id)"
                    class="chat-item"
                  >
                    <a-list-item-meta>
                      <template #title>
                        <div class="chat-title-row">
                          <span class="chat-title">{{ item.title }}</span>
                        </div>
                      </template>
                      <template #description>
                        <div class="chat-desc">{{ item.latest_message || '暂无消息' }}</div>
                      </template>
                    </a-list-item-meta>
                  </a-list-item>
                </template>
              </a-list>
            </div>
          </div>

          <!-- 全屏消息区 -->
          <div class="chat-main-full main-wide">
            <div class="chat-header">
              <div class="header-icon">
                <RobotOutlined />
              </div>
              <div class="header-content">
                <h3 class="chat-title">{{ currentChat?.title || '请选择或新建对话' }}</h3>
                <p class="chat-subtitle">与AI助手开始智能对话</p>
              </div>
            </div>

            <div class="chat-content">
              <div class="messages-wrapper">
                <div class="messages" ref="messagesEl">
                  <template v-if="messages.length">
                    <div v-for="m in messages" :key="m.id" :class="['msg', m.role]">
                      <div class="message-avatar">
                        <a-avatar
                          :size="32"
                          :style="{ backgroundColor: m.role === 'user' ? '#3b82f6' : '#10b981' }"
                        >
                          <template #icon>
                            <UserOutlined v-if="m.role === 'user'" />
                            <RobotOutlined v-else />
                          </template>
                        </a-avatar>
                      </div>
                      <div class="message-content">
                        <div class="bubble">
                          <div class="content">
                            <div
                              v-if="m.id === loadingMessageId && m.role === 'assistant'"
                              class="typing-indicator"
                            >
                              <div class="typing-circle"></div>
                              <div class="typing-circle"></div>
                              <div class="typing-circle"></div>
                              <div class="typing-shadow"></div>
                              <div class="typing-shadow"></div>
                              <div class="typing-shadow"></div>
                            </div>
                            <div v-else v-html="renderContent(m.content)"></div>
                          </div>
                          <div class="time">{{ formatTime(m.created_at) }}</div>
                        </div>
                      </div>
                    </div>
                  </template>
                  <div v-else class="empty-messages">
                    <a-empty description="暂无消息，开始你的第一次对话吧！">
                      <template #image>
                        <MessageOutlined style="font-size: 64px; color: #d9d9d9" />
                      </template>
                    </a-empty>
                  </div>
                </div>
              </div>

              <div class="composer" v-if="currentChatId">
                <div class="input-container">
                  <a-textarea
                    v-model:value="input"
                    :rows="3"
                    placeholder="输入你的问题..."
                    :disabled="!currentChatId"
                    @pressEnter="onEnterSend"
                    class="message-input"
                  />
                  <div class="input-actions">
                    <a-button
                      type="primary"
                      :disabled="!canSend"
                      @click="send"
                      class="send-btn"
                      size="large"
                    >
                      <template #icon>
                        <SendOutlined />
                      </template>
                      发送消息
                    </a-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- 重命名对话模态框 -->
      <a-modal
        v-model:visible="renameOpen"
        title="重命名对话"
        @ok="doRename"
        :confirm-loading="renaming"
        class="rename-modal"
      >
        <a-input v-model:value="renameTitle" placeholder="请输入新标题" />
      </a-modal>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { message } from 'ant-design-vue';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  SendOutlined,
  MessageOutlined,
  RobotOutlined,
  UserOutlined,
  CloseOutlined,
} from '@ant-design/icons-vue';
import dayjs from 'dayjs';
import { aiApi, type AIChatItem, type AIChatDetail, type AIChatMessage } from '@/api/ai';

// AI助手布局配置（三种完全不同的排版样式）
const aiChatLayouts = [
  {
    name: 'default',
    label: '标准布局',
    description: '左右分栏布局，左侧会话列表，右侧消息区，经典聊天界面',
    sidebarClass: 'sidebar-standard',
    mainClass: 'main-standard',
  },
  {
    name: 'compact',
    label: '上下分割布局',
    description: '上部分横向展示会话卡片，下部分消息区，适合需要快速浏览多个会话的场景',
    sidebarClass: 'sidebar-compact',
    mainClass: 'main-compact',
  },
  {
    name: 'wide',
    label: '全屏消息布局',
    description: '全屏显示消息区，侧边栏可折叠悬浮，最大化消息展示区域，专注对话体验',
    sidebarClass: 'sidebar-wide',
    mainClass: 'main-wide',
  },
];

// 侧边栏显示状态（仅用于全屏布局）
const sidebarVisible = ref(false);

// 当前布局
const currentLayout = ref<string>('default');

// 加载布局配置
const loadLayout = () => {
  const savedLayout = localStorage.getItem('aiChatLayout');
  if (savedLayout && aiChatLayouts.find((l) => l.name === savedLayout)) {
    currentLayout.value = savedLayout;
  } else {
    currentLayout.value = 'default';
  }
};

// 监听布局变化事件
const handleLayoutChange = () => {
  loadLayout();
};

// 会话列表状态
const chatList = ref<AIChatItem[]>([]);
const query = ref('');
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);
const loadingChats = ref(false);
const creating = ref(false);

// 当前会话与消息
const currentChatId = ref<number | null>(null);
const currentChat = ref<AIChatDetail | null>(null);
const messages = ref<AIChatMessage[]>([]);
const loadingMessages = ref(false);
const sending = ref(false);

// 错误信息（用于在浏览器中展示HTTP错误详情）
type HttpErrorInfo = {
  status?: number | null;
  message?: string | null;
  url?: string | null;
  method?: string | null;
  requestData?: any;
  data?: any;
} | null;
const errorInfo = ref<HttpErrorInfo>(null);

// 重命名
const renameOpen = ref(false);
const renameTitle = ref('');
const renaming = ref(false);
let renameTargetId: number | null = null;

const messagesEl = ref<HTMLElement | null>(null);
const loadingMessageId = ref<number | null>(null);

const canSend = computed(() => !!currentChatId.value && !!input.value.trim());
const input = ref('');
const searchRef = ref<any>(null);

let tempMessageId = -1;
const createLocalMessage = (role: 'user' | 'assistant', content: string): AIChatMessage => ({
  id: tempMessageId--,
  role,
  content,
  created_at: new Date().toISOString(),
});

const fetchChats = async () => {
  loadingChats.value = true;
  try {
    const res = await aiApi.listChats({
      query: query.value || undefined,
      page: page.value,
      page_size: pageSize.value,
    });
    if (res.success) {
      chatList.value = res.data.chats || [];
      total.value = res.data.total || 0;
      if (!currentChatId.value && chatList.value.length) {
        const firstId = chatList.value[0]?.id;
        if (typeof firstId === 'number' && firstId > 0) {
          selectChat(firstId);
        }
      }
    } else {
      message.error(res.message || '获取对话列表失败');
    }
  } catch (e: any) {
    // 记录错误信息并展示
    errorInfo.value = {
      status: e?.response?.status ?? null,
      message: e?.response?.data?.message || e?.message,
      url: e?.config?.url ?? null,
      method: e?.config?.method ?? 'GET',
      requestData: e?.config?.data,
      data: e?.response?.data,
    };
    if (e?.response?.status === 403) {
      message.warning('暂无权限访问AI助手，请联系管理员开通权限');
    } else {
      message.error(e?.message || '网络错误');
    }
  } finally {
    loadingChats.value = false;
  }
};

const onPageChange = (p: number) => {
  page.value = p;
  fetchChats();
};

const selectChat = async (id: number) => {
  if (typeof id !== 'number' || Number.isNaN(id) || id <= 0) {
    errorInfo.value = {
      status: 404,
      message: '无效的聊天ID',
      url: `/api/ai/chats/${String(id)}/`,
      method: 'GET',
    };
    message.warning('无效的聊天ID，无法加载会话详情');
    return;
  }
  if (currentChatId.value === id && messages.value.length) return;
  currentChatId.value = id;
  loadingMessages.value = true;
  try {
    const res = await aiApi.getChatDetail(id);
    if (res.success) {
      currentChat.value = res.data.chat;
      messages.value = res.data.messages || [];
      await nextTick();
      scrollToBottom();
    } else {
      message.error(res.message || '获取会话详情失败');
    }
  } catch (e: any) {
    errorInfo.value = {
      status: e?.response?.status ?? null,
      message: e?.response?.data?.message || e?.message,
      url: e?.config?.url ?? null,
      method: e?.config?.method ?? 'GET',
      requestData: e?.config?.data,
      data: e?.response?.data,
    };
    message.error(e?.message || '网络错误');
  } finally {
    loadingMessages.value = false;
  }
};

const createChat = async () => {
  creating.value = true;
  try {
    const res = await aiApi.createChat({ title: '新对话' });
    if (res.success) {
      message.success('创建成功');
      await fetchChats();
      const newId =
        typeof (res.data as any)?.id === 'number'
          ? (res.data as any).id
          : Number((res.data as any)?.chat_id);
      if (typeof newId === 'number' && newId > 0) {
        selectChat(newId);
      } else {
        errorInfo.value = {
          status: null,
          message: '创建成功但未返回有效ID',
          url: '/api/ai/chats/create/',
          method: 'POST',
          data: res.data,
        };
      }
    } else {
      message.error(res.message || '创建失败');
    }
  } catch (e: any) {
    errorInfo.value = {
      status: e?.response?.status ?? null,
      message: e?.response?.data?.message || e?.message,
      url: e?.config?.url ?? null,
      method: e?.config?.method ?? 'POST',
      requestData: e?.config?.data,
      data: e?.response?.data,
    };
    message.error(e?.message || '网络错误');
  } finally {
    creating.value = false;
  }
};

const openRename = (item: AIChatItem) => {
  renameTargetId = item.id;
  renameTitle.value = item.title;
  renameOpen.value = true;
};

const doRename = async () => {
  if (!renameTargetId || !renameTitle.value.trim()) {
    message.warning('标题不能为空');
    return;
  }
  renaming.value = true;
  try {
    const res = await aiApi.updateChat(renameTargetId, { title: renameTitle.value.trim() });
    if (res.success) {
      message.success('重命名成功');
      renameOpen.value = false;
      // 同步更新右侧当前会话标题，避免用户误以为未生效
      if (currentChatId.value === renameTargetId && currentChat.value) {
        currentChat.value = { ...currentChat.value, title: renameTitle.value.trim() };
      }
      await fetchChats();
      // 清空输入，防止下次弹窗残留
      renameTitle.value = '';
    } else {
      message.error(res.message || '重命名失败');
    }
  } catch (e: any) {
    message.error(e?.message || '网络错误');
  } finally {
    renaming.value = false;
  }
};

const deleteChat = async (id: number) => {
  try {
    const res = await aiApi.deleteChats([id]);
    if (res.success) {
      message.success('删除成功');
      await fetchChats();
      if (currentChatId.value === id) {
        currentChatId.value = null;
        currentChat.value = null;
        messages.value = [];
      }
    } else {
      message.error(res.message || '删除失败');
    }
  } catch (e: any) {
    message.error(e?.message || '网络错误');
  }
};

const send = async () => {
  if (!canSend.value || !currentChatId.value) return;
  const content = input.value.trim();

  // 本地先插入用户消息
  const userMsg = createLocalMessage('user', content);
  messages.value.push(userMsg);
  input.value = '';
  await nextTick();
  scrollToBottom();

  // 本地插入 AI 加载中消息
  const loadingMsg = createLocalMessage('assistant', 'AI 正在思考中，请稍候...');
  messages.value.push(loadingMsg);
  const loadingId = loadingMsg.id;
  loadingMessageId.value = loadingId;
  await nextTick();
  scrollToBottom();

  try {
    const res = await aiApi.sendMessage(currentChatId.value, { content });
    if (res.success) {
      // 移除加载中消息
      const idx = messages.value.findIndex((m) => m.id === loadingId);
      if (idx !== -1) messages.value.splice(idx, 1);
      // 追加真正的 AI 回复
      messages.value.push(res.data.ai_message);
      await nextTick();
      scrollToBottom();
      fetchChats();
    } else {
      const idx = messages.value.findIndex((m) => m.id === loadingId);
      if (idx !== -1) messages.value.splice(idx, 1);
      message.error(res.message || '发送失败');
    }
  } catch (e: any) {
    const idx = messages.value.findIndex((m) => m.id === loadingId);
    if (idx !== -1) messages.value.splice(idx, 1);
    message.error(e?.message || '网络错误');
  }
  loadingMessageId.value = null;
};

const formatTime = (t: string) => dayjs(t).format('YYYY-MM-DD HH:mm:ss');
const renderContent = (c: string) => c.replace(/\n/g, '<br/>');
const scrollToBottom = () => {
  const el = messagesEl.value;
  if (el) el.scrollTop = el.scrollHeight;
};
const formatJson = (obj: any) => {
  try {
    if (obj == null) return 'null';
    return JSON.stringify(obj, null, 2);
  } catch {
    return String(obj);
  }
};

// 快捷键：回车发送，Shift+Enter 换行（Ant Textarea 的 pressEnter 不会触发 Shift+Enter）
const onEnterSend = () => {
  if (canSend.value) send();
};

// Ctrl+K 聚焦搜索框
const keydownHandler = (e: KeyboardEvent) => {
  if (e.ctrlKey && (e.key === 'k' || e.key === 'K')) {
    e.preventDefault();
    const inst = searchRef.value;
    if (inst && typeof inst.focus === 'function') {
      inst.focus();
    }
  }
};

onMounted(() => {
  loadLayout();
  window.addEventListener('aiChatLayoutChanged', handleLayoutChange);
  window.addEventListener('keydown', keydownHandler);
  fetchChats();
});

onUnmounted(() => {
  window.removeEventListener('keydown', keydownHandler);
  window.removeEventListener('aiChatLayoutChanged', handleLayoutChange);
});
</script>

<style scoped lang="scss">
@import '@/styles/variables';

.ai-chat-page {
  padding: 24px;
  background: var(--theme-page-bg, #f5f5f5);
  min-height: 100vh;

  .page-header {
    margin-bottom: 24px;
    text-align: center;

    .page-title {
      font-size: 2rem;
      font-weight: 700;
      color: var(--theme-text-primary, #1e293b);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;

      .title-icon {
        color: var(--theme-primary, #3b82f6);
      }
    }

    .page-description {
      color: var(--theme-text-secondary, #64748b);
      font-size: 1.1rem;
      margin: 0;
    }
  }

  // 错误提示容器
  .error-container {
    max-width: 1200px;
    margin: 0 auto 24px;
    padding: 0 24px;

    .error-alert {
      border-radius: 12px;
      border: 1px solid #ff4d4f;

      .err-pre {
        margin: 0;
        background: var(--theme-card-bg, #fff);
        border: 1px solid var(--theme-card-border, #f0f0f0);
        border-radius: 4px;
        padding: 6px;
        font-size: 12px;
        max-height: 160px;
        overflow: auto;
      }
    }
  }

  // 聊天容器
  .chat-container {
    max-width: 1200px;
    margin: 0 auto;

    // 操作栏
    .action-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      gap: 16px;
      flex-wrap: wrap;
    }

    // 左侧边栏
    .chat-sidebar {
      background: var(--theme-card-bg, white);
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      border: 1px solid var(--theme-card-border, #e5e7eb);
      display: flex;
      flex-direction: column;
      height: calc(100vh - 200px);
      min-height: 600px;

      .sidebar-header {
        border-bottom: 1px solid var(--theme-card-border, #e5e7eb);
        flex-shrink: 0;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 12px;

        .header-icon {
          width: 36px;
          height: 36px;
          background: linear-gradient(
            135deg,
            var(--theme-primary, #3b82f6) 0%,
            var(--theme-primary, #2563eb) 100%
          );
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 16px;
        }

        .sidebar-title {
          color: var(--theme-text-primary, #1e293b);
          font-size: 16px;
          font-weight: 600;
          margin: 0;
        }
      }

      .chat-list {
        flex: 1;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        padding: 16px;

        .chat-item {
          border-radius: 12px;
          margin-bottom: 8px;
          transition: all 0.3s ease;
          cursor: pointer;

          &:hover {
            background: var(--theme-content-bg, #f8fafc);
          }

          &.active {
            background: var(--theme-content-bg, #eff6ff);
            border: 1px solid var(--theme-primary, #3b82f6);
          }

          .chat-title-row {
            display: flex;
            justify-content: space-between;
            align-items: center;

            .chat-title {
              font-weight: 600;
              color: var(--theme-text-primary, #1e293b);
              flex: 1;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }

            .edit-btn,
            .delete-btn {
              opacity: 0;
              transition: opacity 0.3s ease;
            }

            &:hover .edit-btn,
            &:hover .delete-btn {
              opacity: 1;
            }
          }

          .chat-desc {
            color: var(--theme-text-secondary, #64748b);
            font-size: 12px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            margin-top: 4px;
          }
        }
      }
    }

    // 右侧聊天主区域
    .chat-main {
      background: var(--theme-card-bg, white);
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      border: 1px solid var(--theme-card-border, #e5e7eb);
      display: flex;
      flex-direction: column;
      height: calc(100vh - 200px);
      min-height: 600px;

      .chat-header {
        border-bottom: 1px solid var(--theme-card-border, #e5e7eb);
        flex-shrink: 0;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 12px;

        .header-icon {
          width: 36px;
          height: 36px;
          background: linear-gradient(
            135deg,
            var(--theme-primary, #10b981) 0%,
            var(--theme-primary, #059669) 100%
          );
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 16px;
        }

        .header-content {
          .chat-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--theme-text-primary, #1e293b);
            margin: 0 0 4px 0;
          }

          .chat-subtitle {
            color: var(--theme-text-secondary, #64748b);
            font-size: 14px;
            margin: 0;
          }
        }
      }

      .chat-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        min-height: 0;

        .messages-wrapper {
          flex: 1;
          min-height: 0;
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }

        .messages {
          flex: 1;
          overflow-y: auto;
          overflow-x: hidden;
          padding: 24px;
          background: var(--theme-content-bg, #f8fafc);
          min-height: 0;

          .msg {
            display: flex;
            margin-bottom: 20px;
            gap: 12px;

            .message-avatar {
              flex-shrink: 0;
            }

            .message-content {
              flex: 1;
              max-width: 70%;

              .bubble {
                padding: 16px 20px;
                border-radius: 16px;
                position: relative;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

                .content {
                  font-size: 14px;
                  line-height: 1.6;
                  color: var(--theme-text-primary, #1e293b);

                  // AI 正在思考加载动画（来自 Uiverse.io aaronross1，适配聊天气泡）
                  .typing-indicator {
                    width: 60px;
                    height: 30px;
                    position: relative;
                    z-index: 1;
                  }

                  .typing-circle {
                    width: 8px;
                    height: 8px;
                    position: absolute;
                    border-radius: 50%;
                    background-color: #000;
                    left: 15%;
                    transform-origin: 50%;
                    animation: typing-circle7124 0.5s alternate infinite ease;
                  }

                  .typing-circle:nth-child(2) {
                    left: 45%;
                    animation-delay: 0.2s;
                  }

                  .typing-circle:nth-child(3) {
                    left: auto;
                    right: 15%;
                    animation-delay: 0.3s;
                  }

                  .typing-shadow {
                    width: 5px;
                    height: 4px;
                    border-radius: 50%;
                    background-color: rgba(0, 0, 0, 0.2);
                    position: absolute;
                    top: 30px;
                    transform-origin: 50%;
                    z-index: 0;
                    left: 15%;
                    filter: blur(1px);
                    animation: typing-shadow046 0.5s alternate infinite ease;
                  }

                  .typing-shadow:nth-child(4) {
                    left: 45%;
                    animation-delay: 0.2s;
                  }

                  .typing-shadow:nth-child(5) {
                    left: auto;
                    right: 15%;
                    animation-delay: 0.3s;
                  }
                }

                .time {
                  margin-top: 8px;
                  font-size: 12px;
                  color: var(--theme-text-secondary, #64748b);
                  text-align: right;
                }
              }
            }

            &.user {
              flex-direction: row-reverse;

              .message-content {
                .bubble {
                  background: linear-gradient(
                    135deg,
                    var(--theme-primary, #3b82f6) 0%,
                    var(--theme-primary, #2563eb) 100%
                  );
                  color: white;

                  .content {
                    color: white;
                  }

                  .time {
                    color: rgba(255, 255, 255, 0.8);
                  }
                }
              }
            }

            &.assistant {
              .message-content {
                .bubble {
                  background: var(--theme-card-bg, white);
                  border: 1px solid var(--theme-card-border, #e2e8f0);
                }
              }
            }
          }

          .empty-messages {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
          }
        }

        .composer {
          flex-shrink: 0;
          padding: 20px;
          border-top: 1px solid var(--theme-card-border, #e5e7eb);
          background: var(--theme-card-bg, white);

          .input-container {
            .message-input {
              border-radius: 8px;
              border: 1px solid var(--theme-card-border, #e5e7eb);
            }

            .input-actions {
              display: flex;
              justify-content: flex-end;
              margin-top: 12px;
            }
          }
        }
      }
    }
  }

  // 重命名模态框
  .rename-modal {
    :deep(.ant-modal-content) {
      border-radius: 12px;
    }
  }

  // 布局2：上下分割布局（主题风格）
  .chat-container-vertical {
    display: flex;
    flex-direction: column;
    gap: 16px;
    height: calc(100vh - 200px);
    min-height: 600px;

    .chat-sidebar-vertical {
      background: var(--theme-card-bg, white);
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      border: 1px solid var(--theme-card-border, #e5e7eb);
      padding: 16px;
      flex-shrink: 0;
      max-height: 200px;

      .sidebar-header {
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid var(--theme-card-border, #e5e7eb);

        .header-icon {
          width: 36px;
          height: 36px;
          background: linear-gradient(
            135deg,
            var(--theme-primary, #3b82f6) 0%,
            var(--theme-primary, #2563eb) 100%
          );
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 16px;
        }

        .sidebar-title {
          color: var(--theme-text-primary, #1e293b);
          font-size: 16px;
          font-weight: 600;
          margin: 0;
        }
      }

      .chat-list-horizontal {
        overflow-x: auto;
        overflow-y: hidden;
        padding: 8px 0;
        margin: -8px 0;

        // 滚动条样式
        &::-webkit-scrollbar {
          height: 6px;
        }

        &::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.04);
          border-radius: 3px;
        }

        &::-webkit-scrollbar-thumb {
          background: rgba(0, 0, 0, 0.2);
          border-radius: 3px;

          &:hover {
            background: rgba(0, 0, 0, 0.3);
          }
        }

        :deep(.ant-list) {
          .ant-list-items {
            display: flex;
            gap: 16px;
            flex-wrap: nowrap;
            padding: 8px 0;
          }
        }

        .chat-item-horizontal {
          flex-shrink: 0;
          width: 220px;

          :deep(.ant-card) {
            height: 100%;
            transition: all 0.3s ease;
            border-radius: 8px;
            border: 1px solid var(--theme-card-border, #e5e7eb);
            background: var(--theme-card-bg, white);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);

            &:hover {
              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
              border-color: var(--theme-primary, #3b82f6);
            }

            &.active-card {
              border-color: var(--theme-primary, #3b82f6);
              box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
              background: var(--theme-content-bg, #eff6ff);
            }
          }

          .horizontal-chat-title {
            font-weight: 600;
            color: var(--theme-text-primary, #1e293b);
            margin-bottom: 8px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-size: 14px;
            letter-spacing: -0.2px;
          }

          .horizontal-chat-desc {
            font-size: 12px;
            color: var(--theme-text-secondary, #64748b);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            line-height: 1.4;
          }
        }
      }
    }

    .chat-main-vertical {
      background: var(--theme-card-bg, white);
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      border: 1px solid var(--theme-card-border, #e5e7eb);
      display: flex;
      flex-direction: column;
      flex: 1;
      min-height: 0;

      .chat-header {
        border-bottom: 1px solid var(--theme-card-border, #e5e7eb);
        flex-shrink: 0;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 12px;

        .header-icon {
          width: 36px;
          height: 36px;
          background: linear-gradient(
            135deg,
            var(--theme-primary, #10b981) 0%,
            var(--theme-primary, #059669) 100%
          );
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 16px;
        }

        .header-content {
          .chat-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--theme-text-primary, #1e293b);
            margin: 0 0 4px 0;
          }

          .chat-subtitle {
            color: var(--theme-text-secondary, #64748b);
            font-size: 14px;
            margin: 0;
          }
        }
      }

      // 确保 chat-content 样式与标准布局一致
      .chat-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        min-height: 0;

        .messages-wrapper {
          flex: 1;
          min-height: 0;
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }

        .messages {
          flex: 1;
          overflow-y: auto;
          overflow-x: hidden;
          padding: 24px;
          background: var(--theme-content-bg, #f8fafc);
          min-height: 0;
        }

        .composer {
          flex-shrink: 0;
          padding: 20px;
          border-top: 1px solid var(--theme-card-border, #e5e7eb);
          background: var(--theme-card-bg, white);
        }
      }
    }
  }

  // 布局3：全屏消息布局（主题风格）
  .chat-container-wide {
    position: relative;
    height: calc(100vh - 200px);
    min-height: 600px;

    .sidebar-toggle-btn {
      position: fixed;
      left: 24px;
      top: 50%;
      transform: translateY(-50%);
      z-index: 1000;
      width: 44px;
      height: 44px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
      transition: all 0.3s ease;

      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transform: translateY(-50%) scale(1.05);
      }

      &:active {
        transform: translateY(-50%) scale(0.98);
      }
    }

    .chat-sidebar-floating {
      position: fixed;
      left: -320px;
      top: 50%;
      transform: translateY(-50%);
      width: 320px;
      height: 80vh;
      max-height: 800px;
      background: var(--theme-card-bg, white);
      border-radius: 12px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
      border: 1px solid var(--theme-card-border, #e5e7eb);
      z-index: 999;
      transition: left 0.3s ease;
      display: flex;
      flex-direction: column;
      overflow: hidden;

      &.visible {
        left: 24px;
      }

      .sidebar-header {
        padding: 16px 20px;
        border-bottom: 1px solid var(--theme-card-border, #e5e7eb);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-shrink: 0;

        .header-icon {
          width: 36px;
          height: 36px;
          background: linear-gradient(
            135deg,
            var(--theme-primary, #3b82f6) 0%,
            var(--theme-primary, #2563eb) 100%
          );
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 16px;
        }

        .sidebar-title {
          color: var(--theme-text-primary, #1e293b);
          font-size: 16px;
          font-weight: 600;
          margin: 0;
        }

        .close-sidebar {
          margin-left: auto;
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;

          &:hover {
            background: rgba(0, 0, 0, 0.05);
          }
        }
      }

      .chat-list {
        flex: 1;
        overflow-y: auto;
        padding: 16px;

        // 滚动条样式
        &::-webkit-scrollbar {
          width: 6px;
        }

        &::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.04);
          border-radius: 3px;
        }

        &::-webkit-scrollbar-thumb {
          background: rgba(0, 0, 0, 0.2);
          border-radius: 3px;

          &:hover {
            background: rgba(0, 0, 0, 0.3);
          }
        }
      }
    }

    .chat-main-full {
      background: var(--theme-card-bg, white);
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      border: 1px solid var(--theme-card-border, #e5e7eb);
      display: flex;
      flex-direction: column;
      height: 100%;
      width: 100%;

      .chat-header {
        border-bottom: 1px solid var(--theme-card-border, #e5e7eb);
        flex-shrink: 0;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 12px;

        .header-icon {
          width: 36px;
          height: 36px;
          background: linear-gradient(
            135deg,
            var(--theme-primary, #10b981) 0%,
            var(--theme-primary, #059669) 100%
          );
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 16px;
        }

        .header-content {
          .chat-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--theme-text-primary, #1e293b);
            margin: 0 0 4px 0;
          }

          .chat-subtitle {
            color: var(--theme-text-secondary, #64748b);
            font-size: 14px;
            margin: 0;
          }
        }
      }

      .chat-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        min-height: 0;

        .messages-wrapper {
          flex: 1;
          min-height: 0;
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }

        .messages {
          flex: 1;
          overflow-y: auto;
          overflow-x: hidden;
          padding: 24px;
          background: var(--theme-content-bg, #f8fafc);
          min-height: 0;
        }

        .composer {
          flex-shrink: 0;
          padding: 20px;
          border-top: 1px solid var(--theme-card-border, #e5e7eb);
          background: var(--theme-card-bg, white);
        }
      }
    }
  }
}

@keyframes typing-circle7124 {
  0% {
    top: 20px;
    height: 5px;
    border-radius: 50px 50px 25px 25px;
    transform: scaleX(1.7);
  }

  40% {
    height: 8px;
    border-radius: 50%;
    transform: scaleX(1);
  }

  100% {
    top: 0%;
  }
}

@keyframes typing-shadow046 {
  0% {
    transform: scaleX(1.5);
  }

  40% {
    transform: scaleX(1);
    opacity: 0.7;
  }

  100% {
    transform: scaleX(0.2);
    opacity: 0.4;
  }
}
</style>
