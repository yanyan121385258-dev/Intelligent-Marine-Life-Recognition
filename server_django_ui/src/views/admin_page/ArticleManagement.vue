<template>
  <div class="knowledge-base">
    <!-- 页面头部 - 苹果风格 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon-wrapper">
          <DatabaseOutlined class="header-icon" />
        </div>
        <div class="header-text">
          <h1 class="page-title">文章管理</h1>
          <p class="page-description">集中管理文章内容，支持分类、标签和搜索</p>
        </div>
      </div>
    </div>

    <!-- 操作栏 - 苹果风格 -->
    <div class="action-bar">
      <div class="button-section">
        <a-button type="primary" @click="handleAdd" class="action-btn-primary">
          <template #icon><PlusOutlined /></template>
          新建文档
        </a-button>
        <a-button @click="openCategoryManager" class="action-btn-secondary">
          <template #icon><FolderOpenOutlined /></template>
          分类管理
        </a-button>
        <a-button @click="refreshData" class="action-btn-secondary">
          <template #icon><ReloadOutlined /></template>
          刷新
        </a-button>
        <a-button @click="handleImport" class="action-btn-secondary">
          <template #icon><ImportOutlined /></template>
          导入
        </a-button>
        <a-button @click="handleExport" class="action-btn-secondary">
          <template #icon><ExportOutlined /></template>
          导出
        </a-button>
      </div>

      <div class="search-section">
        <a-input-search
          v-model:value="searchText"
          placeholder="搜索标题、标签或内容"
          style="width: 320px"
          @search="handleSearchImmediate"
          @pressEnter="handleSearchImmediate"
          allow-clear
          :loading="loading"
        >
          <template #enterButton>
            <a-button type="primary">
              <template #icon><SearchOutlined /></template>
              搜索
            </a-button>
          </template>
        </a-input-search>
      </div>
    </div>

    <!-- 内容区：分类树 + 文档列表 -->
    <div class="content-container">
      <a-row :gutter="[8, 16]">
        <!-- 左侧分类树 -->
        <a-col :xs="24" :md="5">
          <div class="category-container">
            <a-card title="分类" size="small" :loading="false" :bordered="false">
              <a-tree
                :tree-data="categoryTree"
                :selected-keys="selectedCategoryKeys"
                @select="onCategorySelect"
                :default-expand-all="true"
                :field-names="{ title: 'title', key: 'key', children: 'children' }"
              />
            </a-card>
          </div>
        </a-col>

        <!-- 右侧文档列表 -->
        <a-col :xs="24" :md="19">
          <div class="table-container">
            <a-card title="文档列表" size="small" :bordered="false">
              <a-table
                :columns="columns"
                :data-source="articles"
                :loading="tableLoading"
                :pagination="pagination"
                row-key="id"
                size="middle"
              >
                <template #bodyCell="{ column, record }">
                  <template v-if="column.key === 'status_display'">
                    <a-tag :color="statusColor(record.status)">
                      {{ record.status_display }}
                    </a-tag>
                  </template>
                  <template v-else-if="column.key === 'actions'">
                    <a-space wrap size="small">
                      <a-button type="link" size="small" @click="handleView(record)">
                        查看
                      </a-button>
                      <a-button type="link" size="small" @click="handleEdit(record)">
                        编辑
                      </a-button>
                      <a-button
                        type="link"
                        size="small"
                        @click="handlePublish(record)"
                        :disabled="record.status === 'published'"
                      >
                        发布
                      </a-button>
                      <a-button
                        type="link"
                        size="small"
                        @click="handleArchive(record)"
                        :disabled="record.status === 'archived'"
                      >
                        归档
                      </a-button>
                      <a-popconfirm title="确认删除该文档？" @confirm="() => handleDelete(record)">
                        <a-button danger type="link" size="small">删除</a-button>
                      </a-popconfirm>
                    </a-space>
                  </template>
                </template>
              </a-table>
            </a-card>
          </div>
        </a-col>
      </a-row>
    </div>

    <!-- 文档详情抽屉 -->
    <a-drawer v-model:visible="detailOpen" title="文档详情" width="720" :destroy-on-close="true">
      <a-descriptions bordered :column="1" v-if="currentDoc">
        <a-descriptions-item label="标题">{{ currentDoc.title }}</a-descriptions-item>
        <a-descriptions-item label="分类">{{ currentDoc.category_name }}</a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="statusColor(currentDoc.status)">{{ currentDoc.status_display }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">{{ currentDoc.created_at }}</a-descriptions-item>
        <a-descriptions-item label="发布时间">{{
          currentDoc.published_at || '-'
        }}</a-descriptions-item>
        <a-descriptions-item
          label="标签"
          v-if="currentDoc.tags_list && currentDoc.tags_list.length"
        >
          <a-space wrap>
            <a-tag v-for="tag in currentDoc.tags_list" :key="tag">{{ tag }}</a-tag>
          </a-space>
        </a-descriptions-item>
        <a-descriptions-item label="摘要" v-if="currentDoc.summary">{{
          currentDoc.summary
        }}</a-descriptions-item>
        <a-descriptions-item label="内容">
          <div class="doc-content">{{ currentDoc.content }}</div>
        </a-descriptions-item>
      </a-descriptions>
    </a-drawer>

    <!-- 新建/编辑文档弹窗 -->
    <a-modal
      v-model:visible="editVisible"
      :title="editMode === 'create' ? '新建文档' : '编辑文档'"
      @ok="handleSave"
      :confirm-loading="saving"
      width="720px"
    >
      <a-form :model="editForm" layout="vertical">
        <a-form-item label="标题" required>
          <a-input v-model:value="editForm.title" placeholder="请输入文档标题" />
        </a-form-item>
        <a-form-item label="分类" required>
          <a-select
            v-model:value="editForm.category"
            :options="categoryOptions"
            placeholder="请选择分类"
          />
        </a-form-item>
        <a-form-item label="标签">
          <a-select
            v-model:value="editForm.tagsArray"
            mode="tags"
            placeholder="输入并回车添加标签"
          />
        </a-form-item>
        <a-form-item label="状态">
          <a-radio-group v-model:value="editForm.status">
            <a-radio value="draft">草稿</a-radio>
            <a-radio value="published">已发布</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="内容">
          <a-textarea
            v-model:value="editForm.content"
            rows="8"
            placeholder="这里是内容编辑区域（可接入富文本编辑器）"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 分类管理弹窗 -->
    <a-modal v-model:visible="categoryVisible" title="分类管理" width="800px" :footer="null">
      <div class="category-toolbar">
        <a-space wrap>
          <a-button type="primary" @click="handleCategoryAdd">
            <template #icon><PlusOutlined /></template>
            新建分类
          </a-button>
          <a-input-search
            v-model:value="categorySearchName"
            placeholder="按名称搜索分类"
            style="width: 280px"
            @search="fetchCategoryListImmediate"
            allow-clear
            :loading="categoryLoading"
          >
            <template #enterButton>
              <a-button type="primary">搜索</a-button>
            </template>
          </a-input-search>
        </a-space>
      </div>

      <a-table
        :columns="categoryColumns"
        :data-source="categoryList"
        :loading="categoryLoading"
        :pagination="categoryPagination"
        row-key="id"
        size="middle"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'children_count'">
            {{ record.children_count ?? 0 }}
          </template>
          <template v-else-if="column.key === 'articles_count'">
            {{ record.articles_count ?? 0 }}
          </template>
          <template v-if="column.key === 'is_active'">
            <a-tag :color="record.is_active ? 'green' : 'red'">
              {{ record.is_active ? '启用' : '停用' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button type="link" size="small" @click="handleCategoryToggleActive(record)">
                {{ record.is_active ? '停用' : '启用' }}
              </a-button>
              <a-button type="link" size="small" @click="handleCategoryEdit(record)">
                编辑
              </a-button>
              <a-popconfirm title="确认删除该分类？" @confirm="() => handleCategoryDelete(record)">
                <a-button danger type="link" size="small">删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>

      <!-- 分类编辑弹窗 -->
      <a-modal
        v-model:visible="categoryEditVisible"
        :title="categoryEditMode === 'create' ? '新建分类' : '编辑分类'"
        @ok="handleCategorySave"
        :confirm-loading="categorySaving"
        width="640px"
      >
        <a-form :model="categoryForm" layout="vertical">
          <a-form-item label="名称" required>
            <a-input v-model:value="categoryForm.name" placeholder="请输入分类名称" />
          </a-form-item>
          <a-form-item label="父级分类">
            <a-select
              v-model:value="categoryForm.parent"
              :options="categoryOptions"
              placeholder="请选择父级分类（可选）"
              allow-clear
            />
          </a-form-item>
          <a-form-item label="排序">
            <a-input-number
              v-model:value="categoryForm.sort_order"
              :min="0"
              :max="9999"
              style="width: 160px"
            />
          </a-form-item>
          <a-form-item label="启用状态">
            <a-switch
              v-model:checked="categoryForm.is_active"
              checked-children="启用"
              un-checked-children="停用"
            />
          </a-form-item>
          <a-form-item label="描述">
            <a-textarea
              v-model:value="categoryForm.description"
              rows="4"
              placeholder="请输入分类描述（可选）"
            />
          </a-form-item>
        </a-form>
      </a-modal>
    </a-modal>

    <!-- 导入弹窗 -->
    <a-modal
      v-model:visible="importVisible"
      title="导入文章"
      :footer="null"
      width="520"
      :destroy-on-close="true"
    >
      <a-form layout="vertical">
        <a-form-item label="目标分类">
          <a-select
            v-model:value="importForm.category_id"
            placeholder="请选择分类（可选）"
            allow-clear
            style="width: 100%"
          >
            <a-select-option v-for="cat in categoryOptions" :key="cat.value" :value="cat.value">
              {{ cat.label }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="导入状态">
          <a-select v-model:value="importForm.status" style="width: 100%">
            <a-select-option value="draft">草稿</a-select-option>
            <a-select-option value="published">已发布</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="选择文件">
          <a-upload
            :show-upload-list="false"
            :before-upload="(file) => { handleImportFile({ file }); return false; }"
            :loading="importLoading"
          >
            <a-button :loading="importLoading">
              <template #icon><ImportOutlined /></template>
              点击选择文件
            </a-button>
          </a-upload>
          <p class="text-sm text-gray-400 mt-2">
            支持格式：Markdown (.md)、HTML (.html)、JSON (.json)
          </p>
        </a-form-item>
        <a-divider />
        <a-form-item label="JSON格式示例">
          <a-textarea
            value='[{"title":"文章标题","content":"文章内容","summary":"文章摘要","status":"draft","tags":"标签1,标签2"}]'
            rows="6"
            :disabled="true"
            class="font-mono text-xs"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue';
import { message } from 'ant-design-vue';
import {
  PlusOutlined,
  ReloadOutlined,
  ImportOutlined,
  ExportOutlined,
  FolderOpenOutlined,
  DatabaseOutlined,
  SearchOutlined,
} from '@ant-design/icons-vue';
import {
  knowledgeApi,
  KnowledgeArticleListItem,
  KnowledgeArticleDetail,
  KnowledgeCategory,
} from '@/api/knowledge';

// 加载状态
const loading = ref(false);

// 搜索
const searchText = ref('');

// 分页（服务端）
const pagination = ref<any>({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  pageSizeOptions: ['10', '20', '50'],
});

// 分类树（接口）
const categoryTree = ref<any[]>([{ title: '全部', key: 'all' }]);
const selectedCategoryKeys = ref<string[]>(['all']);

// 文档列定义（按最新接口）
const columns = [
  { title: '标题', dataIndex: 'title', key: 'title', ellipsis: true },
  { title: '分类', dataIndex: 'category_name', key: 'category_name', ellipsis: true },
  { title: '状态', dataIndex: 'status_display', key: 'status_display' },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    customRender: ({ text }: { text: string }) => formatDateOnly(text),
  },
  {
    title: '发布时间',
    dataIndex: 'published_at',
    key: 'published_at',
    customRender: ({ text }: { text: string }) => (text ? formatDateOnly(text) : '-'),
  },
  { title: '操作', key: 'actions' },
];

// 文档数据（接口）
const articles = ref<KnowledgeArticleListItem[]>([]);
const allArticles = ref<KnowledgeArticleListItem[]>([]); // 存储所有文档数据（用于客户端筛选）

// 列表加载状态（带延迟，避免闪烁）
const tableLoading = computed(() => ({ spinning: loading.value, delay: 200 }));

// 分类选项（用于新建/编辑）
const categoryOptions = computed(() => {
  const flat: { label: string; value: number }[] = [];
  const walk = (nodes: any[]) => {
    nodes.forEach((n: any) => {
      if (n.key !== 'all') {
        flat.push({ label: n.title, value: Number(n.key) });
      }
      if (n.children) walk(n.children);
    });
  };
  walk(categoryTree.value);
  return flat;
});

// 状态颜色
const statusColor = (s: 'draft' | 'published' | 'archived') => {
  switch (s) {
    case 'published':
      return 'green';
    case 'archived':
      return 'orange';
    default:
      return 'blue';
  }
};

// 详情态
const detailOpen = ref(false);
const currentDoc = ref<KnowledgeArticleDetail | null>(null);

// 编辑态
const editVisible = ref(false);
const editMode = ref<'create' | 'update'>('create');
const saving = ref(false);
const editForm = ref<any>({
  id: 0,
  title: '',
  category: undefined as number | undefined,
  tagsArray: [] as string[],
  status: 'draft' as 'draft' | 'published',
  content: '',
  summary: '',
});

onMounted(() => {
  fetchCategories();
  fetchArticles();
});

const fetchCategories = async () => {
  try {
    const res = await knowledgeApi.getCategoryTree();
    const data = (res.data || []) as KnowledgeCategory[];
    const mapNode = (n: KnowledgeCategory): any => ({
      title: n.name,
      key: String(n.id),
      children: (n.children || []).map(mapNode),
    });
    categoryTree.value = [{ title: '全部', key: 'all' }, ...data.map(mapNode)];
  } catch (e) {
    console.error(e);
    // 使用统一错误处理器（已在全局请求拦截中处理），避免重复提示
  }
};

const fetchArticles = async () => {
  loading.value = true;
  try {
    const keyword = searchText.value.trim();
    const needsClientFilter = keyword && keyword.length > 0;

    const params: any = {
      page: needsClientFilter ? 1 : pagination.value.current,
      page_size: needsClientFilter ? 50 : pagination.value.pageSize, // 如果需要客户端筛选，获取更多数据
    };

    // 先尝试后端搜索
    if (keyword) params.title = keyword;

    const selected = selectedCategoryKeys.value[0];
    if (selected && selected !== 'all') params.category_id = Number(selected);

    const res = await knowledgeApi.getArticles(params);
    const d = res.data;
    let allRows = d.list || [];

    // 如果后端不支持搜索或需要客户端筛选，在前端进行筛选
    if (needsClientFilter && keyword) {
      // 保存所有数据用于筛选
      allArticles.value = allRows;

      // 客户端关键字搜索筛选（搜索标题、标签、内容）
      const keywordLower = keyword.toLowerCase();
      allRows = allRows.filter((article: KnowledgeArticleListItem) => {
        const title = (article.title || '').toLowerCase();
        const tags = (article.tags_list || []).join(' ').toLowerCase();
        const summary = (article.summary || '').toLowerCase();
        const categoryName = (article.category_name || '').toLowerCase();
        return (
          title.includes(keywordLower) ||
          tags.includes(keywordLower) ||
          summary.includes(keywordLower) ||
          categoryName.includes(keywordLower)
        );
      });

      // 客户端分页
      const startIndex = (pagination.value.current - 1) * pagination.value.pageSize;
      const endIndex = startIndex + pagination.value.pageSize;
      const paginatedList = allRows.slice(startIndex, endIndex);

      articles.value = paginatedList;
      pagination.value.total = allRows.length;

      console.log('✅ 客户端筛选后总数:', allRows.length, '条');
      console.log('✅ 当前页显示:', paginatedList.length, '条');
    } else {
      // 不需要客户端筛选，直接使用后端返回的数据
      articles.value = allRows;
      allArticles.value = allRows;
      pagination.value.total = d.total;
    }
  } catch (e) {
    console.error(e);
    // 错误统一由拦截器处理
  } finally {
    loading.value = false;
  }
};

const refreshData = () => {
  message.success('已刷新数据');
  fetchArticles();
};

const handleSearchImmediate = () => {
  pagination.value.current = 1;
  fetchArticles();
};

const handleSearch = () => {
  // 输入过程中不立即请求，按需触发
};

const onCategorySelect = (keys: string[]) => {
  selectedCategoryKeys.value = keys;
  pagination.value.current = 1;
  fetchArticles();
};

const handleView = async (record: KnowledgeArticleListItem) => {
  try {
    const res = await knowledgeApi.getArticle(record.id);
    currentDoc.value = res.data;
    detailOpen.value = true;
  } catch (e) {
    console.error(e);
    // 错误统一由拦截器处理
  }
};

const handleAdd = () => {
  editMode.value = 'create';
  editForm.value = {
    id: 0,
    title: '',
    category: undefined,
    tagsArray: [],
    status: 'draft',
    content: '',
    summary: '',
  };
  editVisible.value = true;
};

const handleEdit = async (record: KnowledgeArticleListItem) => {
  editMode.value = 'update';
  try {
    const res = await knowledgeApi.getArticle(record.id);
    const d = res.data;
    editForm.value = {
      id: d.id,
      title: d.title,
      category: d.category,
      tagsArray: d.tags_list || [],
      status: d.status,
      content: d.content,
      summary: d.summary || '',
    };
    editVisible.value = true;
  } catch (e) {
    console.error(e);
    // 错误统一由拦截器处理
  }
};

const handleDelete = async (record: KnowledgeArticleListItem) => {
  try {
    await knowledgeApi.deleteArticle(record.id);
    message.success('已删除');
    fetchArticles();
  } catch (e) {
    console.error(e);
    // 错误统一由拦截器处理
  }
};

const handleSave = async () => {
  saving.value = true;
  try {
    // 基础必填校验与规范化
    const title = String(editForm.value.title || '').trim();
    const content = String(editForm.value.content || '').trim();
    const categoryVal = editForm.value.category;

    if (!title) {
      message.warning('请输入标题');
      return;
    }
    if (!categoryVal) {
      message.warning('请选择分类');
      return;
    }
    if (!content) {
      message.warning('请输入内容');
      return;
    }

    // tags 规范化：去空格、过滤空值、长度限制
    const tagsArray = (editForm.value.tagsArray || [])
      .map((t: any) => String(t).trim())
      .filter((t: string) => !!t);
    let tags = tagsArray.join(',');
    if (tags.length > 200) {
      tags = tags.slice(0, 200);
    }

    const payload: any = {
      title,
      content,
      summary: (editForm.value.summary || '').trim() || undefined,
      category: Number(categoryVal),
      status: editForm.value.status || 'draft',
      tags: tags || undefined,
      sort_order: 0,
    };

    if (editMode.value === 'create') {
      await knowledgeApi.createArticle(payload);
      message.success('创建成功');
    } else {
      await knowledgeApi.updateArticle(editForm.value.id, payload);
      message.success('更新成功');
    }
    editVisible.value = false;
    fetchArticles();
  } catch (e) {
    console.error(e);
    // 422等验证错误的字段提示优化（与全局拦截器互补）
    const d: any = (e as any)?.response?.data;
    if (d?.detail && Array.isArray(d.detail)) {
      const msgs = d.detail.map(
        (it: any) =>
          `${it.loc?.[it.loc.length - 1] || '字段'}: ${it.msg || it.message || '验证失败'}`
      );
      if (msgs.length) message.error(`保存失败：${msgs.join('；')}`);
    } else if (d?.message) {
      message.error(d.message);
    }
  } finally {
    saving.value = false;
  }
};

const handlePublish = async (record: KnowledgeArticleListItem) => {
  try {
    await knowledgeApi.publishArticle(record.id);
    message.success('发布成功');
    fetchArticles();
  } catch (e: any) {
    console.error(e);
    // 错误统一由拦截器处理
  }
};

const handleArchive = async (record: KnowledgeArticleListItem) => {
  try {
    await knowledgeApi.archiveArticle(record.id);
    message.success('归档成功');
    fetchArticles();
  } catch (e) {
    console.error(e);
    // 错误统一由拦截器处理
  }
};

const openCategoryManager = () => {
  categoryVisible.value = true;
  fetchCategoryList();
};

// 导入相关状态
const importVisible = ref(false);
const importLoading = ref(false);
const importForm = reactive({
  category_id: undefined as number | undefined,
  status: 'draft' as 'draft' | 'published',
});

const handleImport = () => {
  importVisible.value = true;
};

const handleImportFile = async (file: any) => {
  importLoading.value = true;
  try {
    const response = await knowledgeApi.importArticle(
      file.file,
      importForm.category_id,
      importForm.status
    );
    
    if (response.success) {
      const count = response.data?.imported_count || 0;
      const errors = response.data?.errors || [];
      
      if (errors.length > 0) {
        message.warning(`导入完成，成功导入 ${count} 篇文章，${errors.length} 篇失败`);
        console.error('导入错误详情:', errors);
      } else {
        message.success(`成功导入 ${count} 篇文章`);
      }
      
      importVisible.value = false;
      fetchArticles();
    } else {
      message.error(response.message || '导入失败');
    }
  } catch (error) {
    console.error('导入失败:', error);
    message.error('导入失败，请检查文件格式');
  } finally {
    importLoading.value = false;
  }
};

const handleExport = () => {
  message.info('导出入口：可支持批量导出为 Markdown/JSON');
};

// 处理分页变更
pagination.value = {
  ...pagination.value,
  onChange: (page: number, pageSize: number) => {
    pagination.value.current = page;
    pagination.value.pageSize = pageSize;

    // 检查是否需要客户端筛选
    const needsClientFilter = searchText.value && searchText.value.trim();

    if (needsClientFilter && allArticles.value.length > 0) {
      // 如果有客户端筛选，直接在前端进行分页
      const keyword = searchText.value.trim().toLowerCase();
      let processedList = allArticles.value.filter((article: KnowledgeArticleListItem) => {
        const title = (article.title || '').toLowerCase();
        const tags = (article.tags_list || []).join(' ').toLowerCase();
        const summary = (article.summary || '').toLowerCase();
        const categoryName = (article.category_name || '').toLowerCase();
        return (
          title.includes(keyword) ||
          tags.includes(keyword) ||
          summary.includes(keyword) ||
          categoryName.includes(keyword)
        );
      });

      // 客户端分页
      const startIndex = (page - 1) * pageSize;
      const endIndex = startIndex + pageSize;
      const paginatedList = processedList.slice(startIndex, endIndex);

      articles.value = paginatedList;
      pagination.value.total = processedList.length;
    } else {
      // 不需要客户端筛选，重新获取数据
      fetchArticles();
    }
  },
  onShowSizeChange: (_: number, size: number) => {
    pagination.value.pageSize = size;
    pagination.value.current = 1;

    // 检查是否需要客户端筛选
    const needsClientFilter = searchText.value && searchText.value.trim();

    if (needsClientFilter && allArticles.value.length > 0) {
      // 如果有客户端筛选，直接在前端进行分页
      const keyword = searchText.value.trim().toLowerCase();
      let processedList = allArticles.value.filter((article: KnowledgeArticleListItem) => {
        const title = (article.title || '').toLowerCase();
        const tags = (article.tags_list || []).join(' ').toLowerCase();
        const summary = (article.summary || '').toLowerCase();
        const categoryName = (article.category_name || '').toLowerCase();
        return (
          title.includes(keyword) ||
          tags.includes(keyword) ||
          summary.includes(keyword) ||
          categoryName.includes(keyword)
        );
      });

      // 客户端分页
      const startIndex = 0;
      const endIndex = size;
      const paginatedList = processedList.slice(startIndex, endIndex);

      articles.value = paginatedList;
      pagination.value.total = processedList.length;
    } else {
      // 不需要客户端筛选，重新获取数据
      fetchArticles();
    }
  },
};

// ---------------- 分类管理逻辑 ----------------
const categoryVisible = ref(false);
const categoryLoading = ref(false);
const categoryList = ref<KnowledgeCategory[]>([]);
const categorySearchName = ref('');
const categoryPagination = ref<any>({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  pageSizeOptions: ['10', '20', '50'],
});
const categoryColumns = [
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '父级', dataIndex: 'parent_name', key: 'parent_name' },
  { title: '排序', dataIndex: 'sort_order', key: 'sort_order' },
  { title: '子分类数', dataIndex: 'children_count', key: 'children_count' },
  { title: '文章数', dataIndex: 'articles_count', key: 'articles_count' },
  { title: '状态', key: 'is_active' },
  { title: '操作', key: 'actions' },
];

const categoryEditVisible = ref(false);
const categoryEditMode = ref<'create' | 'update'>('create');
const categorySaving = ref(false);
const categoryForm = ref<Partial<KnowledgeCategory>>({
  id: 0,
  name: '',
  description: '',
  parent: undefined,
  sort_order: 0,
  is_active: true,
});

const fetchCategoryList = async () => {
  categoryLoading.value = true;
  try {
    const params: any = {
      page: categoryPagination.value.current,
      page_size: categoryPagination.value.pageSize,
    };
    const kw = categorySearchName.value.trim();
    if (kw) params.name = kw;
    const res = await knowledgeApi.getCategories(params);
    const d = res.data;
    categoryList.value = d.list;
    categoryPagination.value.total = d.total;
  } catch (e) {
    console.error(e);
  } finally {
    categoryLoading.value = false;
  }
};

const fetchCategoryListImmediate = () => {
  categoryPagination.value.current = 1;
  fetchCategoryList();
};

categoryPagination.value = {
  ...categoryPagination.value,
  onChange: (page: number, pageSize: number) => {
    categoryPagination.value.current = page;
    categoryPagination.value.pageSize = pageSize;
    fetchCategoryList();
  },
  onShowSizeChange: (_: number, size: number) => {
    categoryPagination.value.pageSize = size;
    categoryPagination.value.current = 1;
    fetchCategoryList();
  },
};

const handleCategoryAdd = () => {
  categoryEditMode.value = 'create';
  categoryForm.value = {
    name: '',
    description: '',
    parent: undefined,
    sort_order: 0,
    is_active: true,
  };
  categoryEditVisible.value = true;
};

const handleCategoryEdit = (record: KnowledgeCategory) => {
  categoryEditMode.value = 'update';
  categoryForm.value = {
    id: record.id,
    name: record.name,
    description: record.description,
    parent: record.parent ?? undefined,
    sort_order: record.sort_order,
    is_active: record.is_active,
  };
  categoryEditVisible.value = true;
};

const handleCategorySave = async () => {
  categorySaving.value = true;
  try {
    const payload: Partial<KnowledgeCategory> = {
      name: categoryForm.value.name || '',
      description: categoryForm.value.description || undefined,
      parent: categoryForm.value.parent ?? undefined,
      sort_order: categoryForm.value.sort_order ?? 0,
      is_active: categoryForm.value.is_active ?? true,
    };

    if (categoryEditMode.value === 'create') {
      await knowledgeApi.createCategory(payload);
      message.success('分类创建成功');
    } else {
      await knowledgeApi.updateCategory(Number(categoryForm.value.id), payload);
      message.success('分类更新成功');
    }
    categoryEditVisible.value = false;
    fetchCategoryList();
    // 同步刷新左侧分类树
    fetchCategories();
  } catch (e) {
    console.error(e);
  } finally {
    categorySaving.value = false;
  }
};

const handleCategoryDelete = async (record: KnowledgeCategory) => {
  try {
    if ((record.children_count ?? 0) > 0) {
      message.warning('该分类下还有子分类，无法删除');
      return;
    }
    await knowledgeApi.deleteCategory(record.id);
    message.success('分类已删除');
    fetchCategoryList();
    fetchCategories();
  } catch (e) {
    console.error(e);
  }
};

const handleCategoryToggleActive = async (record: KnowledgeCategory) => {
  try {
    await knowledgeApi.updateCategory(record.id, { is_active: !record.is_active });
    message.success(record.is_active ? '已停用' : '已启用');
    fetchCategoryList();
    fetchCategories();
  } catch (e) {
    console.error(e);
  }
};

// 仅格式化为日期（YYYY-MM-DD），用于列表展示
const formatDateOnly = (val?: string): string => {
  if (!val) return '-';
  const str = String(val);
  return str.length >= 10 ? str.slice(0, 10) : str;
};
</script>

<style scoped lang="scss">
.knowledge-base {
  padding: 0;
  background: #f5f5f7;
  min-height: 100vh;

  // 页面头部 - 苹果风格
  .page-header {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    padding: 32px 28px;
    margin-bottom: 24px;
    border-radius: 0;
    box-shadow: 0 0.5px 0 rgba(0, 0, 0, 0.08);
    border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);

    .header-content {
      display: flex;
      align-items: center;
      gap: 16px;

      .header-icon-wrapper {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: rgba(99, 102, 241, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

        &:hover {
          transform: scale(1.05);
          background: rgba(99, 102, 241, 0.15);
        }

        .header-icon {
          font-size: 24px;
          color: #6366f1;
        }
      }

      .header-text {
        .page-title {
          font-size: 24px;
          font-weight: 600;
          color: #1d1d1f;
          margin: 0 0 4px 0;
          letter-spacing: -0.3px;
          line-height: 1.2;
        }

        .page-description {
          color: #86868b;
          font-size: 14px;
          margin: 0;
          font-weight: 400;
        }
      }
    }
  }

  // 操作栏 - 苹果风格
  .action-bar {
    margin: 0 28px 24px 28px;
    padding: 20px 24px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-radius: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 0.5px solid rgba(0, 0, 0, 0.08);
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      border-color: rgba(0, 0, 0, 0.12);
    }

    .button-section {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }

    .action-btn-primary {
      border-radius: 12px;
      height: 40px;
      padding: 0 20px;
      font-weight: 500;
      transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
      }

      &:active {
        transform: translateY(0);
      }
    }

    .action-btn-secondary {
      border-radius: 12px;
      height: 40px;
      padding: 0 20px;
      font-weight: 500;
      border-color: rgba(0, 0, 0, 0.12);
      color: #1d1d1f;
      background: rgba(255, 255, 255, 0.8);
      transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

      &:hover {
        background: rgba(0, 0, 0, 0.04);
        border-color: rgba(0, 0, 0, 0.16);
        transform: translateY(-1px);
      }

      &:active {
        transform: translateY(0);
      }
    }

    .search-section {
      display: flex;
      align-items: center;
      gap: 12px;

      :deep(.ant-input-search) {
        .ant-input {
          border-radius: 8px;
          border: 0.5px solid rgba(0, 0, 0, 0.12);
          background: rgba(255, 255, 255, 0.8);
          transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

          &:hover {
            border-color: #3b82f6;
          }

          &:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }
        }

        .ant-btn {
          border-radius: 0 8px 8px 0;
        }
      }
    }
  }

  // 内容容器
  .content-container {
    margin: 0 28px 24px 28px;

    .category-container,
    .table-container {
      background: rgba(255, 255, 255, 0.8);
      backdrop-filter: saturate(180%) blur(20px);
      -webkit-backdrop-filter: saturate(180%) blur(20px);
      border-radius: 16px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      border: 0.5px solid rgba(0, 0, 0, 0.08);
      overflow: hidden;
      transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);

      &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-color: rgba(0, 0, 0, 0.12);
      }
    }

    :deep(.ant-card) {
      background: transparent;
      border: none;
      box-shadow: none;

      .ant-card-head {
        background: rgba(0, 0, 0, 0.02);
        border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
        padding: 16px 20px;

        .ant-card-head-title {
          font-weight: 600;
          color: #1d1d1f;
          font-size: 16px;
        }
      }

      .ant-card-body {
        padding: 20px;
      }
    }

    :deep(.ant-tree) {
      .ant-tree-node-selected {
        background: rgba(99, 102, 241, 0.1);
        border-radius: 8px;
      }

      .ant-tree-title {
        color: #1d1d1f;
        transition: all 0.2s ease;

        &:hover {
          color: #6366f1;
        }
      }
    }

    :deep(.ant-table) {
      background: transparent;

      .ant-table-thead > tr > th {
        background: rgba(0, 0, 0, 0.02);
        font-weight: 600;
        color: #1d1d1f;
        border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
        padding: 6px 8px;
        font-size: 13px;
        letter-spacing: -0.1px;
      }

      .ant-table-tbody > tr {
        transition: all 0.2s ease;

        &:hover > td {
          background: rgba(0, 0, 0, 0.02);
        }

        > td {
          padding: 6px 8px;
          border-bottom: 0.5px solid rgba(0, 0, 0, 0.06);
          color: #1d1d1f;
        }
      }
    }

    // 分页器样式优化 - 苹果风格
    :deep(.ant-pagination) {
      margin: 20px 0;
      padding: 16px 0;
      text-align: center;
      background: rgba(0, 0, 0, 0.02);
      border-top: 0.5px solid rgba(0, 0, 0, 0.08);

      .ant-pagination-total-text {
        color: #86868b;
        font-size: 13px;
        font-weight: 400;
      }

      .ant-pagination-item {
        border-radius: 8px;
        border: 0.5px solid rgba(0, 0, 0, 0.12);
        margin: 0 4px;
        background: rgba(255, 255, 255, 0.8);
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

        &:hover {
          border-color: #3b82f6;
          transform: translateY(-1px);
          box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
        }

        &.ant-pagination-item-active {
          background: #3b82f6;
          border-color: #3b82f6;
          transform: translateY(-1px);
          box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);

          a {
            color: white;
            font-weight: 600;
          }
        }
      }

      .ant-pagination-prev,
      .ant-pagination-next {
        border-radius: 8px;
        margin: 0 8px;
        border: 0.5px solid rgba(0, 0, 0, 0.12);
        background: rgba(255, 255, 255, 0.8);
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

        &:hover {
          border-color: #3b82f6;
          color: #3b82f6;
          transform: translateY(-1px);
          box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
        }
      }

      .ant-select {
        margin: 0 8px;

        .ant-select-selector {
          border-radius: 8px;
          border: 0.5px solid rgba(0, 0, 0, 0.12);
          background: rgba(255, 255, 255, 0.8);
          transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

          &:hover {
            border-color: #3b82f6;
          }
        }
      }
    }
  }

  .doc-content {
    white-space: pre-wrap;
    line-height: 1.75;
    padding: 12px;
    background: rgba(0, 0, 0, 0.02);
    border: 0.5px solid rgba(0, 0, 0, 0.08);
    border-radius: 8px;
    color: #1d1d1f;
  }

  // 分类管理弹窗顶部工具栏间距
  .category-toolbar {
    margin-bottom: 12px;

    :deep(.ant-input-search) {
      .ant-input {
        border-radius: 8px;
        border: 0.5px solid rgba(0, 0, 0, 0.12);
      }
    }
  }

  // 抽屉样式优化
  :deep(.ant-drawer-header) {
    border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
    padding: 20px 24px;

    .ant-drawer-title {
      font-weight: 600;
      color: #1d1d1f;
      font-size: 18px;
    }
  }

  :deep(.ant-drawer-body) {
    padding: 24px;
  }

  :deep(.ant-descriptions) {
    .ant-descriptions-item-label {
      font-weight: 500;
      color: #1d1d1f;
    }

    .ant-descriptions-item-content {
      color: #86868b;
    }
  }

  :deep(.ant-tag) {
    border-radius: 6px;
    font-weight: 500;
    padding: 2px 8px;
  }

  // 分类管理弹窗内的表格样式优化
  :deep(.ant-modal) {
    // 分类管理弹窗内的工具栏
    .category-toolbar {
      margin-bottom: 16px;

      .ant-btn {
        border-radius: 10px;
        height: 40px;
        padding: 0 20px;
        font-weight: 500;
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      }

      .ant-input-search {
        .ant-input {
          border-radius: 10px;
          height: 40px;
        }

        .ant-btn {
          border-radius: 0 10px 10px 0;
          height: 40px;
        }
      }
    }

    // 分类管理弹窗内的表格特殊样式
    .ant-table {
      border-radius: 12px;
      overflow: hidden;

      .ant-table-container {
        border: 0.5px solid rgba(0, 0, 0, 0.08);
        border-radius: 12px;
      }
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .knowledge-base {
    .page-header,
    .action-bar,
    .content-container {
      margin-left: 20px;
      margin-right: 20px;
    }
  }
}

@media (max-width: 768px) {
  .knowledge-base {
    .page-header {
      padding: 24px 16px;

      .header-content {
        .header-icon-wrapper {
          width: 40px;
          height: 40px;

          .header-icon {
            font-size: 20px;
          }
        }

        .header-text {
          .page-title {
            font-size: 20px;
          }

          .page-description {
            font-size: 13px;
          }
        }
      }
    }

    .action-bar {
      margin: 0 16px 20px 16px;
      padding: 16px;
      flex-direction: column;
      align-items: stretch;

      .button-section {
        width: 100%;
        justify-content: flex-start;
      }

      .search-section {
        width: 100%;

        :deep(.ant-input-search) {
          width: 100% !important;
        }
      }
    }

    .content-container {
      margin: 0 16px 20px 16px;

      .category-container,
      .table-container {
        border-radius: 12px;
      }
    }
  }
}
</style>
