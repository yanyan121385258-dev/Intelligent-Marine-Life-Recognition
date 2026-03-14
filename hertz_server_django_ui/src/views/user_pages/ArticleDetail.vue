<template>
  <div class="knowledge-detail">
    <!-- 科技风头部导航 -->
    <div class="tech-header animate-fade-in-up">
      <div class="header-bg">
        <div class="tech-pattern"></div>
        <div class="gradient-overlay"></div>
      </div>
      <div class="header-content">
        <div class="nav-actions">
          <a-button @click="goBack" class="nav-btn back-btn">
            <template #icon><ArrowLeftOutlined /></template>
            返回列表
          </a-button>
          <a-button @click="copyLink" class="nav-btn copy-btn">
            <template #icon><LinkOutlined /></template>
            复制链接
          </a-button>
          <a-button @click="printPage" class="nav-btn print-btn">
            <template #icon><PrinterOutlined /></template>
            打印文章
          </a-button>
        </div>
      </div>
    </div>

    <!-- 文章内容区域 -->
    <div class="article-container">
      <div class="article-wrapper animate-fade-in-up" style="animation-delay: 0.2s">
        <!-- 文章头部信息 -->
        <div class="article-header">
          <div class="article-status">
            <a-tag color="success" class="status-badge" v-if="detail?.status === 'published'">
              <CheckCircleOutlined />
              已发布
            </a-tag>
          </div>

          <h1 class="article-title">{{ detail?.title || '加载中...' }}</h1>

          <div class="article-meta">
            <div class="meta-grid">
              <div class="meta-item">
                <div class="meta-icon">
                  <BookOutlined />
                </div>
                <div class="meta-content">
                  <span class="meta-label">分类</span>
                  <span class="meta-value">{{ detail?.category_name }}</span>
                </div>
              </div>

              <div class="meta-item">
                <div class="meta-icon">
                  <UserOutlined />
                </div>
                <div class="meta-content">
                  <span class="meta-label">作者</span>
                  <span class="meta-value">{{ detail?.author_name }}</span>
                </div>
              </div>

              <div class="meta-item">
                <div class="meta-icon">
                  <CalendarOutlined />
                </div>
                <div class="meta-content">
                  <span class="meta-label">发布时间</span>
                  <span class="meta-value">{{
                    formatDate(detail?.published_at || detail?.created_at)
                  }}</span>
                </div>
              </div>

              <div class="meta-item" v-if="detail?.view_count">
                <div class="meta-icon">
                  <EyeOutlined />
                </div>
                <div class="meta-content">
                  <span class="meta-label">浏览次数</span>
                  <span class="meta-value">{{ detail.view_count }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="article-tags" v-if="detail?.tags_list?.length">
            <div class="tags-label">标签</div>
            <div class="tags-list">
              <a-tag v-for="tag in detail.tags_list" :key="tag" class="tech-tag">
                <TagOutlined />
                {{ tag }}
              </a-tag>
            </div>
          </div>
        </div>

        <!-- 文章内容 -->
        <div class="article-content">
          <a-spin :spinning="loading" size="large">
            <div class="content-wrapper" v-html="detail?.content"></div>
          </a-spin>
        </div>

        <!-- 文章底部操作 -->
        <div class="article-footer">
          <div class="footer-actions">
            <a-button @click="goBack" class="action-btn">
              <template #icon><ArrowLeftOutlined /></template>
              返回列表
            </a-button>
            <a-button @click="copyLink" class="action-btn">
              <template #icon><ShareAltOutlined /></template>
              分享文章
            </a-button>
            <a-button @click="printPage" class="action-btn">
              <template #icon><PrinterOutlined /></template>
              打印
            </a-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import {
  ArrowLeftOutlined,
  LinkOutlined,
  PrinterOutlined,
  CheckCircleOutlined,
  BookOutlined,
  UserOutlined,
  CalendarOutlined,
  EyeOutlined,
  TagOutlined,
  ShareAltOutlined,
} from '@ant-design/icons-vue';
import { knowledgeApi, type KnowledgeArticleDetail } from '@/api/knowledge';

const route = useRoute();
const router = useRouter();
const loading = ref(false);
const detail = ref<KnowledgeArticleDetail | null>(null);

const loadDetail = async () => {
  try {
    loading.value = true;
    const id = Number(route.params.id);
    if (!id) {
      message.error('参数错误');
      goBack();
      return;
    }
    const res = await knowledgeApi.getArticle(id);
    const d = res.data;
    if (d.status !== 'published') {
      message.warning('该文章未发布，无法查看');
      goBack();
      return;
    }
    detail.value = d;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateString: string) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const goBack = () => router.push({ path: '/dashboard', query: { menu: 'knowledge-center' } });
const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href);
    message.success('链接已复制到剪贴板');
  } catch {
    message.error('复制失败，请手动复制链接');
  }
};
const printPage = () => window.print();

onMounted(loadDetail);
</script>

<style scoped lang="scss">
@import '@/styles/variables';

.knowledge-detail {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);

  // 科技风头部导航
  .tech-header {
    position: relative;
    padding: 24px 0;
    margin-bottom: 32px;
    overflow: hidden;

    .header-bg {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #475569 100%);

      .tech-pattern {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image:
          radial-gradient(circle at 25% 25%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
          radial-gradient(circle at 75% 75%, rgba(37, 99, 235, 0.1) 0%, transparent 50%);
        animation: patternFloat 15s ease-in-out infinite;
      }

      .gradient-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(
          135deg,
          rgba(37, 99, 235, 0.1) 0%,
          rgba(59, 130, 246, 0.05) 100%
        );
      }
    }

    .header-content {
      position: relative;
      z-index: 2;
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 24px;

      .nav-actions {
        display: flex;
        gap: 16px;
        justify-content: center;

        .nav-btn {
          border-radius: 12px;
          height: 44px;
          padding: 0 20px;
          font-weight: 600;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          border: 2px solid transparent;

          &.back-btn {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border-color: rgba(255, 255, 255, 0.2);

            &:hover {
              background: rgba(255, 255, 255, 0.2);
              transform: translateY(-2px);
              box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
            }
          }

          &.copy-btn {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            border: none;

            &:hover {
              transform: translateY(-2px);
              box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
            }
          }

          &.print-btn {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            border: none;

            &:hover {
              transform: translateY(-2px);
              box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
            }
          }
        }
      }
    }
  }

  // 文章容器
  .article-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 0 24px;

    .article-wrapper {
      background: white;
      border-radius: 24px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
      border: 1px solid rgba(59, 130, 246, 0.1);
      overflow: hidden;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
      }

      // 文章头部
      .article-header {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 40px;
        border-bottom: 1px solid #e2e8f0;

        .article-status {
          margin-bottom: 24px;

          .status-badge {
            border-radius: 20px;
            font-weight: 600;
            padding: 8px 16px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
          }
        }

        .article-title {
          font-size: 2.5rem;
          font-weight: 800;
          color: #1e293b;
          margin: 0 0 32px 0;
          line-height: 1.2;
          text-align: center;
        }

        .article-meta {
          margin-bottom: 32px;

          .meta-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 24px;

            .meta-item {
              display: flex;
              align-items: center;
              gap: 16px;
              padding: 20px;
              background: white;
              border-radius: 16px;
              border: 1px solid #e2e8f0;
              transition: all 0.3s ease;

              &:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                border-color: #3b82f6;
              }

              .meta-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 20px;
              }

              .meta-content {
                display: flex;
                flex-direction: column;
                gap: 4px;

                .meta-label {
                  font-size: 12px;
                  color: #64748b;
                  font-weight: 500;
                  text-transform: uppercase;
                  letter-spacing: 0.5px;
                }

                .meta-value {
                  font-size: 16px;
                  color: #1e293b;
                  font-weight: 600;
                }
              }
            }
          }
        }

        .article-tags {
          .tags-label {
            font-size: 14px;
            color: #64748b;
            font-weight: 600;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
          }

          .tags-list {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;

            .tech-tag {
              border-radius: 20px;
              padding: 8px 16px;
              font-weight: 500;
              display: flex;
              align-items: center;
              gap: 6px;
              background: linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%);
              color: #0277bd;
              border: 1px solid #81d4fa;
              transition: all 0.3s ease;

              &:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(2, 119, 189, 0.3);
              }
            }
          }
        }
      }

      // 文章内容
      .article-content {
        padding: 40px;

        .content-wrapper {
          font-size: 16px;
          line-height: 1.8;
          color: #374151;
          word-wrap: break-word;
          word-break: break-word;
          overflow-wrap: break-word;
          white-space: pre-wrap;

          // 内容样式优化
          :deep(h1),
          :deep(h2),
          :deep(h3),
          :deep(h4),
          :deep(h5),
          :deep(h6) {
            color: #1e293b;
            font-weight: 700;
            margin: 32px 0 16px 0;
            line-height: 1.3;
            word-wrap: break-word;
            word-break: break-word;
            overflow-wrap: break-word;
          }

          :deep(h1) {
            font-size: 2rem;
          }
          :deep(h2) {
            font-size: 1.75rem;
          }
          :deep(h3) {
            font-size: 1.5rem;
          }
          :deep(h4) {
            font-size: 1.25rem;
          }

          :deep(p) {
            margin: 16px 0;
            text-align: justify;
            word-wrap: break-word;
            word-break: break-word;
            overflow-wrap: break-word;
          }

          :deep(ul),
          :deep(ol) {
            margin: 16px 0;
            padding-left: 24px;
            word-wrap: break-word;
            word-break: break-word;
            overflow-wrap: break-word;

            li {
              margin: 8px 0;
              word-wrap: break-word;
              word-break: break-word;
              overflow-wrap: break-word;
            }
          }

          :deep(blockquote) {
            border-left: 4px solid #3b82f6;
            background: #f8fafc;
            padding: 16px 24px;
            margin: 24px 0;
            border-radius: 0 8px 8px 0;
            font-style: italic;
            color: #64748b;
            word-wrap: break-word;
            word-break: break-word;
            overflow-wrap: break-word;
          }

          :deep(code) {
            background: #f1f5f9;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 14px;
            color: #e11d48;
            word-wrap: break-word;
            word-break: break-word;
            overflow-wrap: break-word;
          }

          :deep(pre) {
            background: #1e293b;
            color: #e2e8f0;
            padding: 24px;
            border-radius: 12px;
            overflow-x: auto;
            margin: 24px 0;

            code {
              background: transparent;
              color: inherit;
              padding: 0;
            }
          }

          :deep(img) {
            max-width: 100%;
            height: auto;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            margin: 24px 0;
          }

          :deep(table) {
            width: 100%;
            border-collapse: collapse;
            margin: 24px 0;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            table-layout: fixed;

            th,
            td {
              padding: 12px 16px;
              text-align: left;
              border-bottom: 1px solid #e2e8f0;
              word-wrap: break-word;
              word-break: break-word;
              overflow-wrap: break-word;
            }

            th {
              background: #f8fafc;
              font-weight: 600;
              color: #1e293b;
            }

            tr:hover {
              background: #f8fafc;
            }
          }
        }
      }

      // 文章底部
      .article-footer {
        background: #f8fafc;
        padding: 32px 40px;
        border-top: 1px solid #e2e8f0;

        .footer-actions {
          display: flex;
          justify-content: center;
          gap: 16px;

          .action-btn {
            border-radius: 12px;
            height: 44px;
            padding: 0 24px;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

            &:hover {
              transform: translateY(-2px);
              box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            }
          }
        }
      }
    }
  }
}

// 科技风动画
@keyframes patternFloat {
  0%,
  100% {
    transform: translate(0, 0) rotate(0deg);
  }
  33% {
    transform: translate(30px, -30px) rotate(120deg);
  }
  66% {
    transform: translate(-20px, 20px) rotate(240deg);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .knowledge-detail {
    .tech-header {
      padding: 16px 0;

      .header-content .nav-actions {
        flex-direction: column;
        align-items: center;
        gap: 12px;

        .nav-btn {
          width: 200px;
        }
      }
    }

    .article-container {
      padding: 0 16px;

      .article-wrapper {
        .article-header {
          padding: 24px;

          .article-title {
            font-size: 2rem;
          }

          .article-meta .meta-grid {
            grid-template-columns: 1fr;
            gap: 16px;

            .meta-item {
              padding: 16px;
            }
          }
        }

        .article-content {
          padding: 24px;
        }

        .article-footer {
          padding: 24px;

          .footer-actions {
            flex-direction: column;
            align-items: center;

            .action-btn {
              width: 200px;
            }
          }
        }
      }
    }
  }
}
</style>
