<template>
  <div class="notice-center">
    <div class="page-header">
      <h1 class="page-title">
        <BellOutlined class="title-icon" />
        通知中心
      </h1>
      <p class="page-description">管理您的通知和消息</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <a-space>
        <a-button
          type="primary"
          :disabled="unreadIds.length === 0"
          @click="markAllRead"
          :loading="batchLoading"
        >
          <template #icon>
            <CheckCircleOutlined />
          </template>
          全部标记为已读
        </a-button>
        <a-button @click="refreshList" :loading="loadingList">
          <template #icon>
            <ReloadOutlined />
          </template>
          刷新
        </a-button>
      </a-space>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-container">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon total">
            <BellOutlined />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.total_count }}</div>
            <div class="stat-label">总消息</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon unread">
            <ExclamationCircleOutlined />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.unread_count }}</div>
            <div class="stat-label">未读消息</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon read">
            <CheckCircleOutlined />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.read_count }}</div>
            <div class="stat-label">已读消息</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon starred">
            <StarOutlined />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.starred_count }}</div>
            <div class="stat-label">收藏消息</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-container">
      <div class="content-wrapper">
        <!-- 标签页 -->
        <div class="tabs-container">
          <a-tabs v-model:activeKey="activeTab" @change="onTabChange" class="tech-tabs">
            <a-tab-pane key="all" tab="全部消息" />
            <a-tab-pane key="unread" tab="未读消息" />
            <a-tab-pane key="starred" tab="收藏消息" />
            <a-tab-pane key="system" tab="系统通知" />
          </a-tabs>
        </div>

        <!-- 空状态提示 -->
        <div v-if="!loadingList && notices.length === 0" class="empty-state">
          <div class="empty-icon">
            <BellOutlined />
          </div>
          <h3 class="empty-title">暂无可见通知</h3>
          <p class="empty-description">{{ emptyHint }}</p>
        </div>

        <!-- 通知列表 -->
        <div v-else class="notices-container">
          <a-list
            :data-source="displayedNotices"
            :loading="loadingList"
            item-layout="vertical"
            class="tech-list"
          >
            <template #renderItem="{ item }">
              <a-list-item class="notice-item">
                <div
                  class="notice-card"
                  :class="{ unread: !item.is_read, starred: item.is_starred }"
                >
                  <div class="notice-header">
                    <div class="notice-icon" :class="iconClass(item.notice_type_display)">
                      <component :is="getIconComponent(item.notice_type_display)" />
                    </div>
                    <div class="notice-content">
                      <div class="title-line">
                        <h3 class="notice-title">{{ item.title }}</h3>
                        <div class="notice-badges">
                          <a-tag v-if="item.is_top" color="red" class="top-tag">置顶</a-tag>
                          <a-tag :color="item.is_read ? 'green' : 'orange'" class="status-tag">
                            {{ item.is_read ? '已读' : '未读' }}
                          </a-tag>
                        </div>
                      </div>
                      <p class="notice-desc">{{ itemDesc(item) }}</p>
                      <div class="notice-meta">
                        <span class="publish-time">
                          <ClockCircleOutlined />
                          {{ item.publish_time }}
                        </span>
                        <div class="notice-actions">
                          <a-button type="link" @click="viewDetail(item)" class="action-link">
                            <EyeOutlined />
                            查看详情
                          </a-button>
                          <a-button
                            type="link"
                            :disabled="item.is_read"
                            @click="markRead(item)"
                            class="action-link"
                          >
                            <CheckCircleOutlined />
                            标记已读
                          </a-button>
                          <a-button type="link" @click="toggleStar(item)" class="action-link">
                            <StarOutlined />
                            {{ item.is_starred ? '取消收藏' : '收藏' }}
                          </a-button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </a-list-item>
            </template>
          </a-list>
        </div>

        <!-- 分页 -->
        <div class="pagination-container">
          <a-pagination
            :current="currentPage"
            :pageSize="pageSize"
            :total="totalCount"
            show-size-changer
            @change="handlePageChange"
            @showSizeChange="handlePageSizeChange"
            class="tech-pagination"
          />
        </div>
      </div>
    </div>

    <!-- 详情模态框 -->
    <a-modal
      v-model:visible="detailVisible"
      title="通知详情"
      width="720px"
      @cancel="closeDetail"
      :footer="null"
      class="detail-modal"
    >
      <a-spin :spinning="detailLoading">
        <div class="detail-content">
          <a-descriptions :column="1" bordered class="tech-descriptions">
            <a-descriptions-item label="标题">
              <span class="detail-title">{{ detailData?.title }}</span>
            </a-descriptions-item>
            <a-descriptions-item label="内容">
              <div class="detail-text">{{ detailData?.content }}</div>
            </a-descriptions-item>
            <a-descriptions-item label="类型">
              <a-tag :color="getTypeColor(detailData?.notice_type_display)">
                {{ detailData?.notice_type_display }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="优先级">
              <a-tag :color="getPriorityColor(detailData?.priority_display)">
                {{ detailData?.priority_display }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="发布时间">
              <span class="detail-time">{{ detailData?.publish_time }}</span>
            </a-descriptions-item>
            <a-descriptions-item label="过期时间">
              <span class="detail-time">{{ detailData?.expire_time || '永久有效' }}</span>
            </a-descriptions-item>
            <a-descriptions-item label="状态信息">
              <div class="status-info">
                <a-tag :color="detailData?.is_top ? 'red' : 'default'">
                  {{ detailData?.is_top ? '置顶' : '普通' }}
                </a-tag>
                <a-tag :color="detailData?.is_starred ? 'gold' : 'default'">
                  {{ detailData?.is_starred ? '已收藏' : '未收藏' }}
                </a-tag>
                <a-tag :color="detailData?.is_read ? 'green' : 'orange'">
                  {{ detailData?.is_read ? '已读' : '未读' }}
                </a-tag>
              </div>
            </a-descriptions-item>
          </a-descriptions>
        </div>
      </a-spin>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { message } from 'ant-design-vue';
import {
  BellOutlined,
  CheckCircleOutlined,
  ReloadOutlined,
  ExclamationCircleOutlined,
  StarOutlined,
  ClockCircleOutlined,
  EyeOutlined,
  SettingOutlined,
  WarningOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons-vue';
import {
  noticeUserApi,
  type UserNoticeListItem,
  type UserNoticeListData,
  type UserNoticeDetailData,
} from '@/api/notice_user';

const loadingList = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const notices = ref<UserNoticeListItem[]>([]);
const totalCount = ref(0);
const batchLoading = ref(false);
const activeTab = ref<'all' | 'unread' | 'starred' | 'system'>('all');

const statistics = reactive({
  total_count: 0,
  unread_count: 0,
  read_count: 0,
  starred_count: 0,
});

const unreadIds = computed(() => notices.value.filter((n) => !n.is_read).map((n) => n.notice));
const displayedNotices = computed(() => {
  let arr = notices.value;
  if (activeTab.value === 'unread') {
    arr = arr.filter((n) => !n.is_read);
  } else if (activeTab.value === 'starred') {
    arr = arr.filter((n) => n.is_starred);
  } else if (activeTab.value === 'system') {
    arr = arr.filter((n) => n.notice_type_display === '系统通知');
  }
  return arr;
});

// 空状态提示文案
const emptyHint = computed(() => {
  if (activeTab.value === 'starred') {
    return '您还没有收藏任何消息。点击消息卡片中的“收藏”按钮可以收藏消息。';
  } else if (activeTab.value === 'unread') {
    return '您没有未读消息。所有消息都已阅读完毕。';
  } else if (activeTab.value === 'system') {
    return '暂无系统通知。';
  }
  return '可能原因：通知未发布或已过期。请联系管理员在“通知管理”中点击“发布”，或调整过期时间后再试。';
});

const fetchStatistics = async () => {
  try {
    const res = await noticeUserApi.statistics();
    if (res.success) {
      const s = res.data;
      statistics.total_count = s.total_count || 0;
      statistics.unread_count = s.unread_count || 0;
      statistics.starred_count = s.starred_count || 0;
      statistics.read_count = s.read_count || s.total_count - s.unread_count;
    }
  } catch (e) {
    // 静默统计失败
  }
};

const fetchList = async () => {
  loadingList.value = true;
  try {
    const res = await noticeUserApi.list({ page: currentPage.value, page_size: pageSize.value });
    if (res.success) {
      notices.value = res.data.notices || [];
      totalCount.value = res.data.pagination?.total_count || 0;
    }
  } catch (e: any) {
    message.error(e?.message || '获取通知列表失败');
  } finally {
    loadingList.value = false;
  }
};

const refreshList = () => {
  fetchList();
  fetchStatistics();
};

const handlePageChange = (page: number) => {
  currentPage.value = page;
  fetchList();
};
const handlePageSizeChange = (_: number, size: number) => {
  pageSize.value = size;
  currentPage.value = 1;
  fetchList();
};
const onTabChange = () => {
  // 标签切换后回到第一页，并刷新当前页数据与统计
  currentPage.value = 1;
  fetchList();
  fetchStatistics();
};

// 左侧图标样式映射
const iconClass = (type: string) => {
  switch (type) {
    case '系统通知':
      return 'icon-system';
    case '安全提醒':
    case '告警':
    case '风险提示':
      return 'icon-warning';
    case '业务通知':
    case '普通通知':
    case '成功':
      return 'icon-success';
    default:
      return 'icon-default';
  }
};

// 获取图标组件
const getIconComponent = (type: string) => {
  switch (type) {
    case '系统通知':
      return SettingOutlined;
    case '安全提醒':
    case '告警':
    case '风险提示':
      return WarningOutlined;
    case '业务通知':
    case '普通通知':
    case '成功':
      return CheckCircleOutlined;
    default:
      return InfoCircleOutlined;
  }
};

// 获取类型颜色
const getTypeColor = (type?: string) => {
  switch (type) {
    case '系统通知':
      return 'blue';
    case '安全提醒':
    case '告警':
    case '风险提示':
      return 'red';
    case '业务通知':
    case '普通通知':
    case '成功':
      return 'green';
    default:
      return 'default';
  }
};

// 获取优先级颜色
const getPriorityColor = (priority?: string) => {
  switch (priority) {
    case '高':
      return 'red';
    case '中':
      return 'orange';
    case '低':
      return 'green';
    default:
      return 'default';
  }
};

// 列表摘要描述（依据文档字段，列表不含正文，展示类型与优先级）
const itemDesc = (item: UserNoticeListItem) => {
  const parts: string[] = [];
  if (item.notice_type_display) parts.push(item.notice_type_display);
  if (item.priority_display) parts.push(item.priority_display);
  return parts.join(' · ');
};

const detailVisible = ref(false);
const detailLoading = ref(false);
const detailData = ref<UserNoticeDetailData | null>(null);

const viewDetail = async (record: UserNoticeListItem) => {
  detailVisible.value = true;
  detailLoading.value = true;
  try {
    const res = await noticeUserApi.detail(record.notice);
    if (res.success) {
      detailData.value = res.data;
    }
  } catch (e: any) {
    message.error(e?.message || '获取通知详情失败');
  } finally {
    detailLoading.value = false;
  }
};

const closeDetail = () => {
  detailVisible.value = false;
  detailData.value = null;
};

const markRead = async (record: UserNoticeListItem) => {
  try {
    const res = await noticeUserApi.markRead(record.notice);
    if (res.success) {
      message.success('已标记为已读');
      refreshList();
    }
  } catch (e: any) {
    message.error(e?.message || '标记已读失败');
  }
};

const markAllRead = async () => {
  const ids = displayedNotices.value.filter((n) => !n.is_read).map((n) => n.notice);
  if (ids.length === 0) return;
  batchLoading.value = true;
  try {
    const res = await noticeUserApi.batchMarkRead(ids);
    if (res.success) {
      message.success(`已标记 ${res.data?.updated_count || ids.length} 条为已读`);
      refreshList();
    }
  } catch (e: any) {
    message.error(e?.message || '批量标记失败');
  } finally {
    batchLoading.value = false;
  }
};

const toggleStar = async (record: UserNoticeListItem) => {
  try {
    const res = await noticeUserApi.toggleStar(record.notice, !record.is_starred);
    if (res.success) {
      message.success(record.is_starred ? '已取消收藏' : '已收藏');
      fetchList();
      fetchStatistics();
    }
  } catch (e: any) {
    message.error(e?.message || '操作失败');
  }
};

onMounted(() => {
  fetchList();
  fetchStatistics();
});
</script>

<style scoped lang="scss">
@import '@/styles/variables';

.notice-center {
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

  // 操作栏
  .action-bar {
    max-width: 1200px;
    margin: 0 auto 16px;
    display: flex;
    justify-content: flex-end;
  }

  // 统计卡片
  .stats-container {
    max-width: 1200px;
    margin: 0 auto 24px;

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 16px;

      .stat-card {
        background: var(--theme-card-bg, white);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid var(--theme-card-border, #e5e7eb);
        display: flex;
        align-items: center;
        gap: 20px;

        .stat-icon {
          width: 56px;
          height: 56px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 24px;

          &.total {
            background: linear-gradient(
              135deg,
              var(--theme-primary, #3b82f6) 0%,
              var(--theme-primary, #2563eb) 100%
            );
          }

          &.unread {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
          }

          &.read {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          }

          &.starred {
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
          }
        }

        .stat-content {
          flex: 1;

          .stat-value {
            font-size: 32px;
            font-weight: 700;
            color: var(--theme-text-primary, #1e293b);
            line-height: 1;
            margin-bottom: 8px;
          }

          .stat-label {
            color: var(--theme-text-secondary, #6b7280);
            font-size: 14px;
          }
        }
      }
    }
  }

  // 主要内容区域
  .main-container {
    max-width: 1200px;
    margin: 0 auto;

    .content-wrapper {
      background: var(--theme-card-bg, white);
      border-radius: 12px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      border: 1px solid var(--theme-card-border, #e5e7eb);

      .tabs-container {
        padding: 0 20px;
        border-bottom: 1px solid var(--theme-card-border, #e5e7eb);

        .tech-tabs {
          :deep(.ant-tabs-nav) {
            margin: 0;
          }
        }
      }

      .empty-state {
        padding: 80px 24px;
        text-align: center;

        .empty-icon {
          width: 80px;
          height: 80px;
          background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 24px;
          color: #64748b;
          font-size: 32px;
        }

        .empty-title {
          font-size: 1.5rem;
          font-weight: 600;
          color: var(--theme-text-primary, #374151);
          margin: 0 0 12px 0;
        }

        .empty-description {
          color: var(--theme-text-secondary, #64748b);
          font-size: 14px;
          line-height: 1.6;
          max-width: 500px;
          margin: 0 auto;
        }
      }

      .notices-container {
        padding: 24px;

        .tech-list {
          :deep(.ant-list-item) {
            padding: 0;
            border: none;
            margin-bottom: 16px;

            &:last-child {
              margin-bottom: 0;
            }
          }

          .notice-item {
            .notice-card {
              background: var(--theme-card-bg, white);
              border-radius: 12px;
              border: 1px solid var(--theme-card-border, #e5e7eb);
              overflow: hidden;

              &.unread {
                border-left: 4px solid #f59e0b;
                background: #fffbeb;
              }

              &.starred {
                border-left: 4px solid #8b5cf6;
                background: #faf5ff;
              }

              .notice-header {
                padding: 20px;
                display: flex;
                gap: 16px;

                .notice-icon {
                  width: 40px;
                  height: 40px;
                  border-radius: 8px;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  color: white;
                  font-size: 18px;
                  flex-shrink: 0;

                  &.icon-system {
                    background: linear-gradient(
                      135deg,
                      var(--theme-primary, #3b82f6) 0%,
                      var(--theme-primary, #2563eb) 100%
                    );
                  }

                  &.icon-warning {
                    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                  }

                  &.icon-success {
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                  }

                  &.icon-default {
                    background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
                  }
                }

                .notice-content {
                  flex: 1;

                  .title-line {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 8px;

                    .notice-title {
                      font-size: 16px;
                      font-weight: 600;
                      color: var(--theme-text-primary, #1e293b);
                      margin: 0;
                      flex: 1;
                    }

                    .notice-badges {
                      display: flex;
                      gap: 8px;

                      .top-tag {
                        margin: 0;
                      }

                      .status-tag {
                        margin: 0;
                      }
                    }
                  }

                  .notice-desc {
                    color: var(--theme-text-secondary, #64748b);
                    font-size: 14px;
                    margin: 0 0 12px 0;
                    line-height: 1.5;
                  }

                  .notice-meta {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 16px;

                    .publish-time {
                      display: flex;
                      align-items: center;
                      gap: 6px;
                      color: #9ca3af;
                      font-size: 12px;
                    }

                    .notice-actions {
                      display: flex;
                      gap: 8px;

                      .action-link {
                        padding: 4px 8px;
                        height: auto;
                        font-size: 12px;
                        color: #64748b;
                        transition: all 0.3s ease;

                        &:hover {
                          color: var(--theme-primary, #3b82f6);
                          background: rgba(59, 130, 246, 0.1);
                          border-radius: 6px;
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }

      .pagination-container {
        padding: 20px;
        border-top: 1px solid var(--theme-card-border, #e5e7eb);
        display: flex;
        justify-content: center;
      }
    }
  }

  // 详情模态框
  .detail-modal {
    :deep(.ant-modal-content) {
      border-radius: 12px;
    }

    .detail-content {
      .tech-descriptions {
        :deep(.ant-descriptions-item-label) {
          font-weight: 600;
          color: var(--theme-text-primary, #374151);
          background: var(--theme-content-bg, #f8fafc);
        }

        :deep(.ant-descriptions-item-content) {
          color: var(--theme-text-primary, #1e293b);
        }

        .detail-title {
          font-size: 16px;
          font-weight: 600;
          color: var(--theme-text-primary, #1e293b);
        }

        .detail-text {
          white-space: pre-wrap;
          word-break: break-word;
          line-height: 1.6;
          color: var(--theme-text-primary, #374151);
        }

        .detail-time {
          color: var(--theme-text-secondary, #64748b);
          font-size: 14px;
        }

        .status-info {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }
      }
    }
  }
}
</style>
