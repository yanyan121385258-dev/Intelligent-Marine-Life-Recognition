<template>
  <div class="knowledge-center">
    <div class="page-header">
      <h1 class="page-title">
        <BookOutlined class="title-icon" />
        文章中心
      </h1>
      <p class="page-description">探索智能知识，提升工作效率</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon">
          <FileTextOutlined />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ pagination.total }}</div>
          <div class="stat-label">文章总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <BookOutlined />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ categoryTree.length }}</div>
          <div class="stat-label">分类数量</div>
        </div>
      </div>
    </div>

    <div class="content-row">
      <a-row :gutter="[16, 16]">
        <!-- 左侧分类树 -->
        <a-col :xs="24" :md="6">
          <div class="category-panel">
            <div class="panel-header">
              <div class="panel-icon">
                <BookOutlined />
              </div>
              <h3 class="panel-title">文章分类</h3>
            </div>
            <div class="panel-content">
              <a-spin :spinning="categoryLoading">
                <a-tree
                  :tree-data="categoryTree"
                  :field-names="{ title: 'name', key: 'id', children: 'children' }"
                  default-expand-all
                  @select="onCategorySelect"
                  class="tech-tree"
                />
              </a-spin>
            </div>
          </div>
        </a-col>

        <!-- 右侧文章列表 -->
        <a-col :xs="24" :md="18">
          <div class="articles-panel">
            <div class="panel-header">
              <div class="header-left">
                <div class="panel-icon">
                  <FileTextOutlined />
                </div>
                <div class="title-group">
                  <h3 class="panel-title">文章列表</h3>
                  <span class="panel-subtitle">发现更多精彩内容</span>
                </div>
              </div>
              <div class="search-section">
                <a-input-search
                  v-model:value="searchText"
                  placeholder="搜索文章标题或标签..."
                  class="tech-search"
                  @search="handleSearchImmediate"
                  @input="handleSearch"
                  allow-clear
                  :loading="loading"
                >
                  <template #prefix>
                    <SearchOutlined class="search-icon" />
                  </template>
                  <template #enterButton>
                    <a-button type="primary" class="search-btn">
                      <SearchOutlined />
                    </a-button>
                  </template>
                </a-input-search>
              </div>
            </div>

            <div class="panel-content">
              <a-spin :spinning="loading">
                <div class="articles-grid" v-if="articleList.length > 0">
                  <div
                    v-for="(item, index) in articleList"
                    :key="item.id"
                    class="article-card"
                    @click="openDetail(item.id)"
                  >
                    <div class="card-header">
                      <div class="article-status">
                        <a-tag color="success" class="status-tag">
                          <CheckCircleOutlined />
                          已发布
                        </a-tag>
                      </div>
                      <div class="article-views" v-if="item.view_count">
                        <EyeOutlined />
                        <span>{{ item.view_count }}</span>
                      </div>
                    </div>

                    <div class="card-body">
                      <h4 class="article-title">{{ item.title }}</h4>
                      <p class="article-summary" v-if="item.summary">{{ item.summary }}</p>
                    </div>

                    <div class="card-footer">
                      <div class="article-meta">
                        <div class="meta-item">
                          <BookOutlined />
                          <span>{{ item.category_name }}</span>
                        </div>
                        <div class="meta-item">
                          <UserOutlined />
                          <span>{{ item.author_name }}</span>
                        </div>
                        <div class="meta-item">
                          <ClockCircleOutlined />
                          <span>{{ formatDate(item.published_at || item.updated_at) }}</span>
                        </div>
                      </div>
                      <div class="read-more">
                        <ReadOutlined />
                        <span>阅读全文</span>
                      </div>
                    </div>
                  </div>
                </div>

                <a-empty v-else description="暂无文章数据" class="empty-state">
                  <template #image>
                    <FileSearchOutlined style="font-size: 64px; color: #d9d9d9" />
                  </template>
                </a-empty>
              </a-spin>

              <!-- 分页 -->
              <div class="pagination-wrapper" v-if="pagination.total > 0">
                <a-pagination
                  v-model:current="pagination.current"
                  v-model:page-size="pagination.pageSize"
                  :total="pagination.total"
                  :show-size-changer="true"
                  :show-quick-jumper="true"
                  :show-total="(total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`"
                  @change="pagination.onChange"
                  class="tech-pagination"
                />
              </div>
            </div>
          </div>
        </a-col>
      </a-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import {
  BookOutlined,
  FileTextOutlined,
  EyeOutlined,
  ReadOutlined,
  SearchOutlined,
  CheckCircleOutlined,
  UserOutlined,
  ClockCircleOutlined,
  FileSearchOutlined,
} from '@ant-design/icons-vue';
import {
  knowledgeApi,
  type KnowledgeArticleListItem,
  type KnowledgeArticleDetail,
  type KnowledgeCategory,
} from '@/api/knowledge';

const loading = ref(false);
const categoryLoading = ref(false);
const searchText = ref('');
const router = useRouter();

const categoryTree = ref<KnowledgeCategory[]>([]);
const selectedCategoryId = ref<number | undefined>(undefined);

const articleList = ref<KnowledgeArticleListItem[]>([]);
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  onChange: (page: number, pageSize: number) => {
    pagination.current = page;
    pagination.pageSize = pageSize;
    fetchArticles();
  },
});

// 详情页改为独立路由展示

const fetchCategories = async () => {
  try {
    categoryLoading.value = true;
    const res = await knowledgeApi.getCategoryTree();
    categoryTree.value = (res.data || []).filter((c: any) => c.is_active !== false);
  } catch (e) {
    console.error(e);
  } finally {
    categoryLoading.value = false;
  }
};

const fetchArticles = async () => {
  try {
    loading.value = true;
    const res = await knowledgeApi.getArticles({
      page: pagination.current,
      page_size: pagination.pageSize,
      title: searchText.value || undefined,
      category_id: selectedCategoryId.value,
      status: 'published',
    });
    const data = res.data;
    articleList.value = data?.list || [];
    pagination.total = data?.total || 0;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const handleSearchImmediate = () => {
  pagination.current = 1;
  fetchArticles();
};

const handleSearch = () => {
  // 防抖可选，这里直接刷新列表
  pagination.current = 1;
  fetchArticles();
};

const onCategorySelect = (keys: (string | number)[]) => {
  selectedCategoryId.value = (keys[0] as number) || undefined;
  pagination.current = 1;
  fetchArticles();
};

const formatDate = (dateString: string) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

const openDetail = async (id: number) => {
  try {
    const res = await knowledgeApi.getArticle(id);
    const detail = res.data;
    if (detail.status !== 'published') {
      message.warning('该文章未发布，无法查看');
      return;
    }
    router.push(`/user/knowledge/${id}`);
  } catch (e) {
    console.error(e);
  }
};

onMounted(() => {
  fetchCategories();
  fetchArticles();
});
</script>

<style scoped lang="scss">
@import '@/styles/variables';

.knowledge-center {
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

  // 统计卡片
  .stats-section {
    max-width: 1200px;
    margin: 0 auto 24px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
        background: linear-gradient(
          135deg,
          var(--theme-primary, #3b82f6) 0%,
          var(--theme-primary, #2563eb) 100%
        );
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
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

  .content-row {
    max-width: 1200px;
    margin: 0 auto;
  }

  // 分类面板
  .category-panel {
    background: var(--theme-card-bg, white);
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--theme-card-border, #e5e7eb);
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 500px;

    .panel-header {
      border-bottom: 1px solid var(--theme-card-border, #e5e7eb);
      flex-shrink: 0;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      gap: 12px;

      .panel-icon {
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

      .panel-title {
        color: var(--theme-text-primary, #1e293b);
        font-size: 16px;
        font-weight: 600;
        margin: 0;
      }
    }

    .panel-content {
      flex: 1;
      overflow-y: auto;
      padding: 20px;

      .tech-tree {
        :deep(.ant-tree-node-content-wrapper) {
          border-radius: 6px;
          padding: 6px 10px;

          &:hover {
            background: var(--theme-content-bg, #eff6ff);
          }

          &.ant-tree-node-selected {
            background: var(--theme-content-bg, #eff6ff);
            color: var(--theme-primary, #2563eb);
          }
        }
      }
    }
  }

  // 文章面板
  .articles-panel {
    background: var(--theme-card-bg, white);
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--theme-card-border, #e5e7eb);

    .panel-header {
      border-bottom: 1px solid var(--theme-card-border, #e5e7eb);
      padding: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;

      .header-left {
        display: flex;
        align-items: center;
        gap: 12px;

        .panel-icon {
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

        .title-group {
          .panel-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--theme-text-primary, #1e293b);
            margin: 0 0 4px 0;
          }

          .panel-subtitle {
            color: var(--theme-text-secondary, #64748b);
            font-size: 14px;
          }
        }
      }

      .search-section {
        .tech-search {
          width: 300px;
        }
      }
    }

    .panel-content {
      padding: 24px;

      .articles-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 16px;
        margin-bottom: 24px;

        .article-card {
          background: var(--theme-card-bg, white);
          border-radius: 12px;
          border: 1px solid var(--theme-card-border, #e5e7eb);
          overflow: hidden;
          cursor: pointer;
          transition: all 0.3s ease;

          &:hover {
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
            border-color: var(--theme-primary, #3b82f6);
          }

          .card-header {
            padding: 20px 20px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;

            .article-status {
              .status-tag {
                border-radius: 20px;
                font-weight: 500;
                padding: 4px 12px;
                display: flex;
                align-items: center;
                gap: 6px;
              }
            }

            .article-views {
              display: flex;
              align-items: center;
              gap: 6px;
              color: var(--theme-text-secondary, #64748b);
              font-size: 14px;
              font-weight: 500;
            }
          }

          .card-body {
            padding: 16px 20px;

            .article-title {
              font-size: 18px;
              font-weight: 700;
              color: var(--theme-text-primary, #1e293b);
              margin: 0 0 12px 0;
              line-height: 1.4;
              display: -webkit-box;
              -webkit-line-clamp: 2;
              -webkit-box-orient: vertical;
              overflow: hidden;
            }

            .article-summary {
              color: var(--theme-text-secondary, #64748b);
              font-size: 14px;
              line-height: 1.6;
              margin: 0;
              display: -webkit-box;
              -webkit-line-clamp: 3;
              -webkit-box-orient: vertical;
              overflow: hidden;
            }
          }

          .card-footer {
            padding: 0 20px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;

            .article-meta {
              display: flex;
              flex-direction: column;
              gap: 8px;

              .meta-item {
                display: flex;
                align-items: center;
                gap: 8px;
                color: var(--theme-text-secondary, #64748b);
                font-size: 13px;
                font-weight: 500;
              }
            }

            .read-more {
              display: flex;
              align-items: center;
              gap: 6px;
              color: var(--theme-text-secondary, #94a3b8);
              font-size: 14px;
              font-weight: 600;
              transition: all 0.3s ease;
            }
          }
        }
      }

      .empty-state {
        padding: 60px 20px;
        text-align: center;

        :deep(.ant-empty-description) {
          color: var(--theme-text-secondary, #64748b);
          font-size: 16px;
        }
      }

      .pagination-wrapper {
        display: flex;
        justify-content: center;
        margin-top: 24px;
        padding-top: 20px;
        border-top: 1px solid var(--theme-card-border, #e5e7eb);
      }
    }
  }
}
</style>
