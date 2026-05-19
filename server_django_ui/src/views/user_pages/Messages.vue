<template>
  <div class="messages-page">
    <a-card title="消息中心" class="messages-card">
      <template #extra>
        <a-space>
          <a-button @click="markAllAsRead" :disabled="unreadCount === 0"> 全部标记为已读 </a-button>
          <a-badge :count="unreadCount">
            <BellOutlined style="font-size: 16px" />
          </a-badge>
        </a-space>
      </template>

      <a-tabs v-model:activeKey="activeTab" @change="handleTabChange">
        <a-tab-pane key="all" tab="全部消息">
          <a-list
            :data-source="filteredMessages"
            :pagination="{ pageSize: 10 }"
            item-layout="horizontal"
          >
            <template #renderItem="{ item }">
              <a-list-item :class="{ 'unread-message': !item.read }" @click="markAsRead(item)">
                <a-list-item-meta>
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: getTypeColor(item.type) }">
                      <component :is="getTypeIcon(item.type)" />
                    </a-avatar>
                  </template>
                  <template #title>
                    <div class="message-title">
                      <span>{{ item.title }}</span>
                      <a-tag v-if="!item.read" color="red" size="small">未读</a-tag>
                    </div>
                  </template>
                  <template #description>
                    <div class="message-content">
                      <p>{{ item.content }}</p>
                      <span class="message-time">{{ formatTime(item.created_at) }}</span>
                    </div>
                  </template>
                </a-list-item-meta>
                <template #actions>
                  <a-button type="link" size="small" @click.stop="deleteMessage(item.id)">
                    删除
                  </a-button>
                </template>
              </a-list-item>
            </template>
          </a-list>
        </a-tab-pane>

        <a-tab-pane key="unread" tab="未读消息">
          <a-list
            :data-source="unreadMessages"
            :pagination="{ pageSize: 10 }"
            item-layout="horizontal"
          >
            <template #renderItem="{ item }">
              <a-list-item @click="markAsRead(item)">
                <a-list-item-meta>
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: getTypeColor(item.type) }">
                      <component :is="getTypeIcon(item.type)" />
                    </a-avatar>
                  </template>
                  <template #title>
                    <div class="message-title">
                      <span>{{ item.title }}</span>
                      <a-tag color="red" size="small">未读</a-tag>
                    </div>
                  </template>
                  <template #description>
                    <div class="message-content">
                      <p>{{ item.content }}</p>
                      <span class="message-time">{{ formatTime(item.created_at) }}</span>
                    </div>
                  </template>
                </a-list-item-meta>
                <template #actions>
                  <a-button type="link" size="small" @click.stop="deleteMessage(item.id)">
                    删除
                  </a-button>
                </template>
              </a-list-item>
            </template>
          </a-list>
        </a-tab-pane>

        <a-tab-pane key="system" tab="系统通知">
          <a-list
            :data-source="systemMessages"
            :pagination="{ pageSize: 10 }"
            item-layout="horizontal"
          >
            <template #renderItem="{ item }">
              <a-list-item :class="{ 'unread-message': !item.read }" @click="markAsRead(item)">
                <a-list-item-meta>
                  <template #avatar>
                    <a-avatar style="background-color: #1890ff">
                      <NotificationOutlined />
                    </a-avatar>
                  </template>
                  <template #title>
                    <div class="message-title">
                      <span>{{ item.title }}</span>
                      <a-tag v-if="!item.read" color="red" size="small">未读</a-tag>
                    </div>
                  </template>
                  <template #description>
                    <div class="message-content">
                      <p>{{ item.content }}</p>
                      <span class="message-time">{{ formatTime(item.created_at) }}</span>
                    </div>
                  </template>
                </a-list-item-meta>
                <template #actions>
                  <a-button type="link" size="small" @click.stop="deleteMessage(item.id)">
                    删除
                  </a-button>
                </template>
              </a-list-item>
            </template>
          </a-list>
        </a-tab-pane>
      </a-tabs>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import {
  BellOutlined,
  NotificationOutlined,
  UserOutlined,
  WarningOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons-vue';
import dayjs from 'dayjs';

interface Message {
  id: number;
  title: string;
  content: string;
  type: 'system' | 'user' | 'warning' | 'success';
  read: boolean;
  created_at: string;
}

const activeTab = ref('all');

const messages = ref<Message[]>([
  {
    id: 1,
    title: '系统维护通知',
    content: '系统将于今晚22:00-24:00进行维护，期间可能无法正常访问，请提前做好准备。',
    type: 'system',
    read: false,
    created_at: '2024-01-15T10:30:00',
  },
  {
    id: 2,
    title: '密码即将过期',
    content: '您的密码将在7天后过期，请及时修改密码以确保账户安全。',
    type: 'warning',
    read: false,
    created_at: '2024-01-14T15:20:00',
  },
  {
    id: 3,
    title: '项目审核通过',
    content: '恭喜！您提交的项目"用户管理系统"已通过审核，可以开始正式开发。',
    type: 'success',
    read: true,
    created_at: '2024-01-13T09:15:00',
  },
  {
    id: 4,
    title: '新用户注册',
    content: '有新用户注册了您的应用，请及时查看用户信息。',
    type: 'user',
    read: false,
    created_at: '2024-01-12T14:45:00',
  },
]);

const filteredMessages = computed(() => {
  switch (activeTab.value) {
    case 'unread':
      return messages.value.filter((msg) => !msg.read);
    case 'system':
      return messages.value.filter((msg) => msg.type === 'system');
    default:
      return messages.value;
  }
});

const unreadMessages = computed(() => {
  return messages.value.filter((msg) => !msg.read);
});

const systemMessages = computed(() => {
  return messages.value.filter((msg) => msg.type === 'system');
});

const unreadCount = computed(() => {
  return messages.value.filter((msg) => !msg.read).length;
});

const getTypeColor = (type: Message['type']) => {
  const colors = {
    system: '#1890ff',
    user: '#52c41a',
    warning: '#faad14',
    success: '#52c41a',
  };
  return colors[type];
};

const getTypeIcon = (type: Message['type']) => {
  const icons = {
    system: NotificationOutlined,
    user: UserOutlined,
    warning: WarningOutlined,
    success: CheckCircleOutlined,
  };
  return icons[type];
};

const formatTime = (time: string) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm');
};

const markAsRead = (msg: Message) => {
  if (!msg.read) {
    msg.read = true;
    message.success('消息已标记为已读');
  }
};

const markAllAsRead = () => {
  const unreadMessages = messages.value.filter((msg) => !msg.read);
  unreadMessages.forEach((msg) => {
    msg.read = true;
  });
  if (unreadMessages.length > 0) {
    message.success(`已将 ${unreadMessages.length} 条消息标记为已读`);
  }
};

const deleteMessage = (id: number) => {
  const index = messages.value.findIndex((msg) => msg.id === id);
  if (index > -1) {
    messages.value.splice(index, 1);
    message.success('消息删除成功');
  }
};

const handleTabChange = (key: string) => {
  activeTab.value = key;
};

onMounted(() => {
  // 这里可以调用获取消息列表的API
});
</script>

<style scoped lang="scss">
.messages-page {
  padding: 24px;

  .messages-card {
    .unread-message {
      background-color: #f6ffed;
      border-left: 3px solid #52c41a;
    }

    .message-title {
      display: flex;
      align-items: center;
      justify-content: space-between;

      span {
        font-weight: 500;
      }
    }

    .message-content {
      p {
        margin: 0 0 8px 0;
        color: #666;
      }

      .message-time {
        font-size: 12px;
        color: #999;
      }
    }

    :deep(.ant-list-item) {
      cursor: pointer;
      transition: background-color 0.3s;

      &:hover {
        background-color: #f5f5f5;
      }
    }
  }
}
</style>
