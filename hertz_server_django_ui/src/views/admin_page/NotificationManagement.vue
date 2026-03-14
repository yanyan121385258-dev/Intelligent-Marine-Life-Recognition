<template>
  <div class="notification-management">
    <!-- 页面头部 - 苹果风格 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon-wrapper">
          <BellOutlined class="header-icon" />
        </div>
        <div class="header-text">
          <h1 class="page-title">通知管理</h1>
          <p class="page-description">管理系统通知和公告</p>
        </div>
      </div>
    </div>

    <!-- 操作栏 - 苹果风格 -->
    <div class="action-bar">
      <div class="search-section">
        <a-input
          v-model:value="searchKeyword"
          placeholder="搜索通知标题、内容..."
          style="width: 300px"
          @pressEnter="handleSearch"
          allow-clear
        />
        <a-button
          type="primary"
          class="search-btn"
          style="margin-left: 12px"
          :loading="loading"
          @click="handleSearch"
        >
          查询
        </a-button>
        <a-select
          v-model:value="statusFilter"
          placeholder="状态筛选"
          style="width: 120px; margin-left: 12px"
          allow-clear
          @change="handleSearch"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option :value="1">草稿</a-select-option>
          <a-select-option :value="2">已发布</a-select-option>
          <a-select-option :value="3">已过期</a-select-option>
        </a-select>
        <a-select
          v-model:value="typeFilter"
          placeholder="类型筛选"
          style="width: 120px; margin-left: 12px"
          allow-clear
          @change="handleSearch"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option :value="1">系统通知</a-select-option>
          <a-select-option :value="2">公告</a-select-option>
        </a-select>
      </div>
      <div class="button-section">
        <a-button type="primary" @click="handleAdd" class="action-btn-primary">
          <template #icon><PlusOutlined /></template>
          添加通知
        </a-button>
        <a-button
          danger
          :disabled="selectedRowKeys.length === 0"
          @click="handleBatchDelete"
          class="action-btn-danger"
        >
          <template #icon><DeleteOutlined /></template>
          批量删除
        </a-button>
        <a-button @click="refreshData" class="action-btn-secondary">
          <template #icon><ReloadOutlined /></template>
          刷新
        </a-button>
      </div>
    </div>

    <!-- 通知表格 -->
    <div class="table-container">
      <a-table
        :columns="columns"
        :data-source="noticeList"
        :loading="loading"
        :pagination="pagination"
        :row-selection="rowSelection"
        row-key="notice_id"
        @change="handleTableChange"
        size="middle"
      >
        <!-- 标题列 -->
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'title'">
            <div class="title-container">
              <span class="title-text">{{ formatTitleShort(record.title) }}</span>
              <span v-if="record.is_top" class="top-tag">置顶</span>
            </div>
          </template>

          <!-- 状态列 -->
          <template v-else-if="column.key === 'status'">
            <a-tag :color="getStatusColor(getStatusCode(record))">
              {{ record.status_display ?? getStatusText(getStatusCode(record)) }}
            </a-tag>
          </template>

          <!-- 通知类型列 -->
          <template v-else-if="column.key === 'notice_type'">
            <a-tag :color="getTypeColor(record.notice_type)">
              {{ getTypeText(record.notice_type) }}
            </a-tag>
          </template>

          <!-- 优先级列 -->
          <template v-else-if="column.key === 'priority'">
            <a-tag :color="getPriorityColor(record.priority)">
              {{ getPriorityText(record.priority) }}
            </a-tag>
          </template>

          <!-- 操作列 -->
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleViewDetail(record)">
                查看详情
              </a-button>
              <a-button type="link" size="small" @click="handleEdit(record)"> 编辑 </a-button>
              <a-button
                type="link"
                size="small"
                :disabled="false"
                @click="handlePublish(record.notice_id)"
              >
                发布
              </a-button>
              <a-button
                type="link"
                size="small"
                :disabled="false"
                @click="handleWithdraw(record.notice_id)"
              >
                撤销发布
              </a-button>
              <a-popconfirm
                title="确定要删除这个通知吗？"
                ok-text="确定"
                cancel-text="取消"
                @confirm="handleDelete(record.notice_id)"
              >
                <a-button type="link" size="small" danger> 删除 </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 添加/编辑通知弹窗 -->
    <a-modal
      v-model:visible="modalVisible"
      :title="modalTitle"
      :confirm-loading="modalLoading"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
      width="700px"
    >
      <a-form ref="formRef" :model="formData" :rules="formRules" layout="vertical">
        <a-form-item label="通知标题" name="title">
          <a-input v-model:value="formData.title" placeholder="请输入通知标题" />
        </a-form-item>

        <a-form-item label="通知内容" name="content">
          <a-textarea v-model:value="formData.content" placeholder="请输入通知内容" rows="6" />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="通知类型" name="notice_type">
              <a-select v-model:value="formData.notice_type" placeholder="请选择通知类型">
                <a-select-option :value="1">系统通知</a-select-option>
                <a-select-option :value="2">公告</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="优先级" name="priority">
              <a-select v-model:value="formData.priority" placeholder="请选择优先级">
                <a-select-option :value="1">低</a-select-option>
                <a-select-option :value="2">中</a-select-option>
                <a-select-option :value="3">高</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="是否置顶" name="is_top">
              <a-switch v-model:checked="formData.is_top" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="过期时间" name="expire_time">
              <a-date-picker
                v-model:value="formData.expire_time"
                show-time
                placeholder="请选择过期时间"
                style="width: 100%"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DDTHH:mm:ss"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="状态" name="status" v-if="modalMode === 'edit'">
          <a-select v-model:value="formData.status" placeholder="请选择状态">
            <a-select-option :value="1">草稿</a-select-option>
            <a-select-option :value="2">已发布</a-select-option>
            <a-select-option :value="3">已过期</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 通知详情弹窗 -->
    <a-modal v-model:visible="detailVisible" title="通知详情" :footer="null" width="700px">
      <a-spin :spinning="detailLoading">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="通知标题">
            {{ notificationDetail?.title }}
          </a-descriptions-item>
          <a-descriptions-item label="通知内容">
            <div class="detail-content">{{ notificationDetail?.content }}</div>
          </a-descriptions-item>
          <a-descriptions-item label="通知类型">
            <a-tag :color="notificationDetail ? getTypeColor(notificationDetail.notice_type) : ''">
              {{ notificationDetail ? getTypeText(notificationDetail.notice_type) : '' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="优先级">
            <a-tag :color="notificationDetail ? getPriorityColor(notificationDetail.priority) : ''">
              {{ notificationDetail ? getPriorityText(notificationDetail.priority) : '' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="是否置顶">
            {{ notificationDetail?.is_top ? '是' : '否' }}
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag
              :color="notificationDetail ? getStatusColor(getStatusCode(notificationDetail)) : ''"
            >
              {{ notificationDetail ? getStatusText(getStatusCode(notificationDetail)) : '' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="过期时间">
            {{ notificationDetail?.expire_time || '永久有效' }}
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">
            {{ notificationDetail?.create_time }}
          </a-descriptions-item>
          <a-descriptions-item label="更新时间">
            {{ notificationDetail?.update_time }}
          </a-descriptions-item>
        </a-descriptions>
      </a-spin>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { request } from '@/utils/hertz_request';
import { message } from 'ant-design-vue';
import { PlusOutlined, ReloadOutlined, BellOutlined, DeleteOutlined } from '@ant-design/icons-vue';
import type { TableColumnsType, TableProps } from 'ant-design-vue';
import { Modal } from 'ant-design-vue';

// 定义通知数据类型
interface NoticeItem {
  id?: number;
  notice_id: number;
  title: string;
  content: string;
  notice_type: number;
  priority: number;
  is_top: boolean;
  status: number;
  expire_time?: string;
  create_time?: string;
  created_at?: string;
  update_time?: string;
  updated_at?: string;
  [key: string]: any;
}

interface NoticeListResponse {
  success: boolean;
  code: number;
  message: string;
  data: {
    notices: NoticeItem[];
    pagination: {
      current_page: number;
      page_size: number;
      total_count: number;
      total_pages: number;
      has_next: boolean;
      has_previous: boolean;
    };
  };
}

interface NoticeDetailResponse {
  success: boolean;
  code: number;
  message: string;
  data: NoticeItem;
}

interface CommonResponse {
  success: boolean;
  code: number;
  message: string;
  data?: any;
}

// 表格列定义（为避免横向滚动，控制每列更紧凑的宽度）
const columns = [
  {
    title: '通知标题',
    dataIndex: 'title',
    key: 'title',
    ellipsis: true,
    width: 80,
  },
  {
    title: '通知类型',
    dataIndex: 'notice_type',
    key: 'notice_type',
    width: 80,
  },
  {
    title: '优先级',
    dataIndex: 'priority',
    key: 'priority',
    width: 70,
  },
  {
    title: '是否置顶',
    dataIndex: 'is_top',
    key: 'is_top',
    width: 70,
    customRender: ({ text }) => (text ? '是' : '否'),
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 80,
  },
  {
    title: '创建时间',
    dataIndex: 'create_time',
    key: 'create_time',
    width: 90,
    customRender: ({ text }) => formatDateOnly(text as string),
  },
  {
    title: '过期时间',
    dataIndex: 'expire_time',
    key: 'expire_time',
    width: 90,
    customRender: ({ text }) => (text ? formatDateOnly(text as string) : '永久有效'),
  },
  {
    title: '操作',
    key: 'action',
    fixed: 'right',
    width: 210,
  },
];

// 响应式数据
const noticeList = ref<NoticeItem[]>([]);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const totalCount = ref(0);
const selectedRowKeys = ref<number[]>([]);
const searchKeyword = ref('');
const statusFilter = ref<number | ''>('');
const typeFilter = ref<number | ''>('');
// 存储所有通知数据（用于客户端筛选）
const allNotices = ref<NoticeItem[]>([]);

// 弹窗相关
const modalVisible = ref(false);
const modalLoading = ref(false);
const modalMode = ref<'add' | 'edit'>('add');
const modalTitle = computed(() => (modalMode.value === 'add' ? '添加通知' : '编辑通知'));

const detailVisible = ref(false);
const detailLoading = ref(false);
const notificationDetail = ref<NoticeItem | null>(null);

// 表单数据
const formRef = ref<any>(null);
const formData = reactive({
  id: 0,
  title: '',
  content: '',
  notice_type: 1,
  priority: 2,
  is_top: false,
  status: 1,
  expire_time: undefined as string | undefined,
});

// 表单验证规则
const formRules = {
  title: [
    { required: true, message: '请输入通知标题', trigger: 'blur' },
    { max: 100, message: '通知标题不能超过100个字符', trigger: 'blur' },
  ],
  content: [{ required: true, message: '请输入通知内容', trigger: 'blur' }],
  notice_type: [{ required: true, message: '请选择通知类型', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
};

// 分页配置
const pagination = ref({
  current: currentPage.value,
  pageSize: pageSize.value,
  total: totalCount.value,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number, range: [number, number]) =>
    `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
  pageSizeOptions: ['10', '20', '50', '100'],
  onChange: (page: number) => {
    currentPage.value = page;
    fetchNoticeList();
  },
  onShowSizeChange: (current: number, size: number) => {
    currentPage.value = current;
    pageSize.value = size;
    fetchNoticeList();
  },
});

// 行选择配置
const rowSelection: TableProps['rowSelection'] = {
  selectedRowKeys: selectedRowKeys,
  onChange: (keys: number[]) => {
    selectedRowKeys.value = keys;
  },
};

// 获取状态文本
const getStatusText = (status: number): string => {
  const statusMap: Record<number, string> = {
    1: '草稿',
    2: '已发布',
    3: '已过期',
  };
  return statusMap[status] || '未知';
};

// 将文本状态映射为数值代码（兼容中英文与后端显示字段）
const mapStatusTextToCode = (text?: any): number => {
  if (text == null) return 0;
  const s = String(text).toLowerCase();
  if (s.includes('草稿') || s.includes('draft')) return 1;
  if (s.includes('已发布') || s.includes('published')) return 2;
  if (s.includes('已过期') || s.includes('expired')) return 3;
  return 0;
};

// 统一获取记录的状态代码，兼容 number、字符串和 status_display
const getStatusCode = (record: any): number => {
  const raw = record?.status;
  if (typeof raw === 'number') return raw;
  // 兼容字符串形式的数字，如 '1'、'2'、'3'
  const asNum = Number(raw);
  if (!isNaN(asNum) && asNum > 0) return asNum;
  return mapStatusTextToCode(record?.status_display ?? raw);
};

// 获取状态颜色
const getStatusColor = (status: number): string => {
  const colorMap: Record<number, string> = {
    1: 'default',
    2: 'green',
    3: 'red',
  };
  return colorMap[status] || 'default';
};

// 获取类型文本
const getTypeText = (type: number): string => {
  const typeMap: Record<number, string> = {
    1: '系统通知',
    2: '公告',
  };
  return typeMap[type] || '未知';
};

// 获取类型颜色
const getTypeColor = (type: number): string => {
  const colorMap: Record<number, string> = {
    1: 'blue',
    2: 'purple',
  };
  return colorMap[type] || 'default';
};

// 获取优先级文本
const getPriorityText = (priority: number): string => {
  const priorityMap: Record<number, string> = {
    1: '低',
    2: '中',
    3: '高',
  };
  return priorityMap[priority] || '未知';
};

// 获取优先级颜色
const getPriorityColor = (priority: number): string => {
  const colorMap: Record<number, string> = {
    1: 'green',
    2: 'orange',
    3: 'red',
  };
  return colorMap[priority] || 'default';
};

// 仅格式化为日期（YYYY-MM-DD），用于列表展示
const formatDateOnly = (val?: string): string => {
  if (!val) return '-';
  const str = String(val);
  return str.length >= 10 ? str.slice(0, 10) : str;
};

// 通知标题仅保留前4个字符，多余用 ... 表示
const formatTitleShort = (val?: string): string => {
  if (!val) return '-';
  const str = String(val);
  return str.length <= 4 ? str : str.slice(0, 4) + '...';
};

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields();
  }
  Object.assign(formData, {
    id: 0,
    title: '',
    content: '',
    notice_type: 1,
    priority: 2,
    is_top: false,
    status: 1,
    expire_time: undefined,
  });
};

// 获取通知列表
// 在获取通知列表后添加额外的调试日志
const fetchNoticeList = async () => {
  try {
    loading.value = true;

    // 检查是否需要客户端筛选（如果后端不支持这些参数）
    const needsClientFilter =
      (searchKeyword.value && searchKeyword.value.trim()) ||
      (statusFilter.value !== '' &&
        statusFilter.value !== null &&
        statusFilter.value !== undefined) ||
      (typeFilter.value !== '' && typeFilter.value !== null && typeFilter.value !== undefined);

    // 构建查询参数
    const params: any = {
      page: needsClientFilter ? 1 : currentPage.value,
      page_size: needsClientFilter ? 1000 : pageSize.value, // 如果需要客户端筛选，获取更多数据
    };

    // 添加搜索参数（先尝试后端搜索）
    if (searchKeyword.value && searchKeyword.value.trim()) {
      params.search = searchKeyword.value.trim();
    }

    // 添加状态筛选
    if (
      statusFilter.value !== '' &&
      statusFilter.value !== null &&
      statusFilter.value !== undefined
    ) {
      params.status = statusFilter.value;
    }

    // 添加类型筛选
    if (typeFilter.value !== '' && typeFilter.value !== null && typeFilter.value !== undefined) {
      params.notice_type = typeFilter.value;
    }

    console.log('🔍 搜索参数:', params);
    console.log('🔍 搜索关键词:', searchKeyword.value);
    console.log('🔍 状态筛选:', statusFilter.value);
    console.log('🔍 类型筛选:', typeFilter.value);
    console.log('🔍 需要客户端筛选:', needsClientFilter);

    const response = await request.get<NoticeListResponse>('/api/notice/admin/list/', {
      params,
    });

    if (response.success && response.data) {
      // 处理数据，确保每个记录都有正确的id映射
      let processedList = response.data.notices.map((notice) => {
        const createTime = notice.create_time || notice.created_at;
        const updateTime = notice.update_time || notice.updated_at;

        return {
          ...notice,
          create_time: createTime,
          update_time: updateTime,
          // 规范化状态，兼容 status_display 或字符串状态
          status: getStatusCode(notice),
          notice_id: Number(notice.notice_id),
          id: Number(notice.notice_id), // 映射notice_id到id，兼容现有代码，并统一为数字
        };
      });

      // 如果后端不支持搜索或筛选，在前端进行客户端筛选
      if (needsClientFilter) {
        // 保存所有数据用于筛选
        allNotices.value = processedList;

        // 客户端搜索筛选
        if (searchKeyword.value && searchKeyword.value.trim()) {
          const keyword = searchKeyword.value.trim().toLowerCase();
          processedList = processedList.filter((notice: NoticeItem) => {
            const title = (notice.title || '').toLowerCase();
            const content = (notice.content || '').toLowerCase();
            return title.includes(keyword) || content.includes(keyword);
          });
        }

        // 客户端状态筛选
        if (
          statusFilter.value !== '' &&
          statusFilter.value !== null &&
          statusFilter.value !== undefined
        ) {
          processedList = processedList.filter((notice: NoticeItem) => {
            return getStatusCode(notice) === statusFilter.value;
          });
        }

        // 客户端类型筛选
        if (
          typeFilter.value !== '' &&
          typeFilter.value !== null &&
          typeFilter.value !== undefined
        ) {
          processedList = processedList.filter((notice: NoticeItem) => {
            return notice.notice_type === typeFilter.value;
          });
        }

        // 客户端分页
        const startIndex = (currentPage.value - 1) * pageSize.value;
        const endIndex = startIndex + pageSize.value;
        const paginatedList = processedList.slice(startIndex, endIndex);

        noticeList.value = paginatedList;
        totalCount.value = processedList.length; // 使用筛选后的总数
        pagination.value.total = processedList.length;
        pagination.value.current = currentPage.value;

        console.log('✅ 客户端筛选后总数:', processedList.length, '条');
        console.log('✅ 当前页显示:', paginatedList.length, '条');
      } else {
        // 不需要客户端筛选，直接使用后端返回的数据
        noticeList.value = processedList;
        totalCount.value = response.data.pagination.total_count;
        // 更新分页配置
        pagination.value.current = response.data.pagination.current_page;
        pagination.value.total = response.data.pagination.total_count;
        console.log('✅ 获取到通知列表:', noticeList.value.length, '条');
      }

      // 调试日志，查看返回的数据结构
      console.log('原始通知列表数据:', response.data.notices);
      console.log('处理后通知列表数据:', noticeList.value);
    } else {
      message.error(response.message || '获取通知列表失败');
    }
  } catch (error) {
    console.error('获取通知列表失败:', error);
    message.error('获取通知列表失败');
  } finally {
    loading.value = false;
  }
};

// 处理编辑
const handleEdit = (record: NoticeItem) => {
  console.log('编辑记录完整结构:', JSON.stringify(record, null, 2));
  // 增强ID检查逻辑，直接使用notice_id
  if (record && record.notice_id) {
    modalMode.value = 'edit';
    Object.assign(formData, {
      ...record,
      status: getStatusCode(record),
      id: record.notice_id, // 直接使用notice_id作为id
    });
    console.log('设置表单数据:', formData);
    modalVisible.value = true;
  } else {
    console.warn('无法编辑：通知ID无效');
  }
};

// 处理查看详情
const handleViewDetail = (record: NoticeItem) => {
  console.log('查看详情记录完整结构:', JSON.stringify(record, null, 2));
  // 增强ID检查逻辑，直接使用notice_id
  if (record && record.notice_id) {
    console.log('使用ID查看详情:', record.notice_id);
    fetchNoticeDetail(record.notice_id);
    detailVisible.value = true;
  } else {
    console.warn('无法查看详情：通知ID无效');
  }
};

// 获取通知详情
const fetchNoticeDetail = async (id: number) => {
  try {
    detailLoading.value = true;
    const response = await request.get<NoticeDetailResponse>(`/api/notice/admin/detail/${id}/`);
    if (response.success && response.data) {
      const data = response.data;
      const createTime = data.create_time || data.created_at;
      const updateTime = data.update_time || data.updated_at;
      notificationDetail.value = {
        ...data,
        create_time: createTime,
        update_time: updateTime,
      };
    }
  } catch (error) {
    console.error('获取通知详情失败:', error);
  } finally {
    detailLoading.value = false;
  }
};

// 创建通知
const createNotice = async (data: any) => {
  try {
    modalLoading.value = true;
    const response = await request.post<CommonResponse>('/api/notice/admin/create/', data);
    return response;
  } catch (error) {
    console.error('创建通知失败:', error);
    throw error;
  } finally {
    modalLoading.value = false;
  }
};

// 更新通知
const updateNotice = async (id: number, data: any) => {
  try {
    modalLoading.value = true;
    const response = await request.put<CommonResponse>(`/api/notice/admin/update/${id}/`, data);
    return response;
  } catch (error) {
    console.error('更新通知失败:', error);
    throw error;
  } finally {
    modalLoading.value = false;
  }
};

// 删除通知
const deleteNotice = async (id: number) => {
  try {
    const response = await request.delete<CommonResponse>(`/api/notice/admin/delete/${id}/`);
    return response;
  } catch (error) {
    console.error('删除通知失败:', error);
    throw error;
  }
};

// 发布通知
const publishNotice = async (id: number) => {
  try {
    const response = await request.post<CommonResponse>(`/api/notice/admin/publish/${id}/`);
    return response;
  } catch (error) {
    console.error('发布通知失败:', error);
    throw error;
  }
};

// 撤销发布
const withdrawNotice = async (id: number) => {
  try {
    const response = await request.post<CommonResponse>(`/api/notice/admin/withdraw/${id}/`);
    return response;
  } catch (error) {
    console.error('撤销发布失败:', error);
    throw error;
  }
};

// 处理添加通知
const handleAdd = () => {
  modalMode.value = 'add';
  resetForm();
  modalVisible.value = true;
};

// 处理删除
const handleDelete = async (id: number) => {
  if (!id || id <= 0) {
    console.warn('无法删除：通知ID无效');
    return;
  }
  try {
    const response = await deleteNotice(id);
    if (response.success) {
      fetchNoticeList();
      message.success('删除成功');
    } else {
      message.error(response.message || '删除失败');
    }
  } catch (error) {
    console.error('删除通知失败:', error);
    message.error('删除失败');
  }
};

// 处理发布
const handlePublish = async (id: number) => {
  if (!id || id <= 0) {
    console.warn('无法发布：通知ID无效');
    return;
  }
  try {
    const response = await publishNotice(id);
    if (response.success) {
      fetchNoticeList();
      message.success('发布成功');
    } else {
      message.error(response.message || '发布失败');
    }
  } catch (error) {
    console.error('发布通知失败:', error);
    message.error('发布失败');
  }
};

// 处理撤销发布
const handleWithdraw = async (id: number) => {
  if (!id || id <= 0) {
    console.warn('无法撤销发布：通知ID无效');
    return;
  }
  // 总是尝试撤销，由后端进行最终校验；同时输出调试信息便于定位
  const noticeRecord = noticeList.value.find((notice) => String(notice.notice_id) === String(id));
  console.log('准备撤销发布，记录：', noticeRecord);
  console.log('状态代码：', noticeRecord ? getStatusCode(noticeRecord) : 'unknown');

  try {
    const response = await withdrawNotice(id);
    if (response.success) {
      fetchNoticeList();
      message.success('已撤销发布');
    } else {
      message.error(response.message || '撤销失败');
    }
  } catch (error) {
    console.error('撤销发布失败:', error);
    message.error('撤销失败');
  }
};

// 处理弹窗确定
const handleModalOk = async () => {
  if (formRef.value) {
    try {
      await formRef.value.validate();
      let response;
      if (modalMode.value === 'add') {
        response = await createNotice(formData);
      } else {
        // 添加ID有效性检查
        if (!formData.id || formData.id <= 0) {
          console.warn('更新失败：通知ID无效');
          return;
        }
        response = await updateNotice(formData.id, formData);
      }
      if (response.success) {
        modalVisible.value = false;
        fetchNoticeList();
        message.success(modalMode.value === 'add' ? '创建成功' : '更新成功');
      }
    } catch (error) {
      console.error('保存通知失败:', error);
      message.error('保存失败');
    }
  }
};

// 处理弹窗取消
const handleModalCancel = () => {
  modalVisible.value = false;
  resetForm();
};

// 处理表格变化
const handleTableChange = (pag: any) => {
  currentPage.value = pag.current;
  pageSize.value = pag.pageSize;

  // 检查是否需要客户端筛选
  const needsClientFilter =
    (searchKeyword.value && searchKeyword.value.trim()) ||
    (statusFilter.value !== '' &&
      statusFilter.value !== null &&
      statusFilter.value !== undefined) ||
    (typeFilter.value !== '' && typeFilter.value !== null && typeFilter.value !== undefined);

  if (needsClientFilter && allNotices.value.length > 0) {
    // 如果有客户端筛选，直接在前端进行分页
    let processedList = [...allNotices.value];

    // 客户端搜索筛选
    if (searchKeyword.value && searchKeyword.value.trim()) {
      const keyword = searchKeyword.value.trim().toLowerCase();
      processedList = processedList.filter((notice: NoticeItem) => {
        const title = (notice.title || '').toLowerCase();
        const content = (notice.content || '').toLowerCase();
        return title.includes(keyword) || content.includes(keyword);
      });
    }

    // 客户端状态筛选
    if (
      statusFilter.value !== '' &&
      statusFilter.value !== null &&
      statusFilter.value !== undefined
    ) {
      processedList = processedList.filter((notice: NoticeItem) => {
        return getStatusCode(notice) === statusFilter.value;
      });
    }

    // 客户端类型筛选
    if (typeFilter.value !== '' && typeFilter.value !== null && typeFilter.value !== undefined) {
      processedList = processedList.filter((notice: NoticeItem) => {
        return notice.notice_type === typeFilter.value;
      });
    }

    // 客户端分页
    const startIndex = (pag.current - 1) * pag.pageSize;
    const endIndex = startIndex + pag.pageSize;
    const paginatedList = processedList.slice(startIndex, endIndex);

    noticeList.value = paginatedList;
    totalCount.value = processedList.length;
    pagination.value.total = processedList.length;
    pagination.value.current = pag.current;
  } else {
    // 不需要客户端筛选，重新获取数据
    fetchNoticeList();
  }
};

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1;
  fetchNoticeList();
};

// 批量删除
const handleBatchDelete = () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请选择要删除的通知');
    return;
  }

  Modal.confirm({
    title: '确认批量删除',
    content: `确定要删除选中的 ${selectedRowKeys.value.length} 个通知吗？此操作不可恢复。`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        loading.value = true;
        const deletePromises = selectedRowKeys.value.map((id) => deleteNotice(id));

        const results = await Promise.allSettled(deletePromises);
        const successCount = results.filter(
          (r) => r.status === 'fulfilled' && r.value.success
        ).length;
        const failCount = results.length - successCount;

        if (successCount > 0) {
          message.success(
            `成功删除 ${successCount} 个通知${failCount > 0 ? `，${failCount} 个删除失败` : ''}`
          );
          selectedRowKeys.value = [];
          await fetchNoticeList();
        } else {
          message.error('批量删除失败，请重试');
        }
      } catch (error) {
        console.error('批量删除失败:', error);
        message.error('批量删除失败');
      } finally {
        loading.value = false;
      }
    },
  });
};

// 刷新数据
const refreshData = () => {
  searchKeyword.value = '';
  statusFilter.value = '';
  typeFilter.value = '';
  selectedRowKeys.value = [];
  currentPage.value = 1;
  fetchNoticeList();
};

// 组件挂载时获取数据
onMounted(() => {
  fetchNoticeList();
});
</script>

<style scoped lang="scss">
.notification-management {
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
        background: rgba(250, 112, 154, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

        &:hover {
          transform: scale(1.05);
          background: rgba(250, 112, 154, 0.15);
        }

        .header-icon {
          font-size: 24px;
          color: #fa709a;
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
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      border-color: rgba(0, 0, 0, 0.12);
    }

    .search-section {
      display: flex;
      align-items: center;
      flex: 1;

      :deep(.ant-input-search) {
        .ant-input-affix-wrapper {
          border-radius: 12px;
          border: 0.5px solid rgba(0, 0, 0, 0.12);
          background: rgba(255, 255, 255, 0.8);
          transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

          &:hover {
            border-color: #3b82f6;
          }

          &.ant-input-affix-wrapper-focused {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }
        }

        .ant-input-search-button {
          border-radius: 0 12px 12px 0;
          border-left: none;
        }
      }

      :deep(.ant-select) {
        .ant-select-selector {
          border-radius: 12px;
          border: 0.5px solid rgba(0, 0, 0, 0.12);
          background: rgba(255, 255, 255, 0.8);
          transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

          &:hover {
            border-color: #3b82f6;
          }
        }

        &.ant-select-focused .ant-select-selector {
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
      }
    }

    .button-section {
      display: flex;
      gap: 12px;

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

      .action-btn-danger {
        border-radius: 12px;
        height: 40px;
        padding: 0 20px;
        font-weight: 500;
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

        &:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        }

        &:active:not(:disabled) {
          transform: translateY(0);
        }

        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
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
    }
  }

  // 表格容器 - 苹果风格
  .table-container {
    margin: 0 28px 24px 28px;
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

    .title-container {
      display: flex;
      align-items: center;

      .title-text {
        flex: 1;
        font-weight: 500;
        color: #1d1d1f;
      }

      .top-tag {
        margin-left: 8px;
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #fff;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(250, 112, 154, 0.3);
      }
    }

    // 分页器样式优化 - 苹果风格
    :deep(.ant-pagination) {
      margin: 20px 24px;
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

      .ant-pagination-jump-prev,
      .ant-pagination-jump-next {
        border-radius: 8px;
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

      .ant-pagination-options-quick-jumper {
        margin-left: 16px;
        color: #86868b;
        font-size: 13px;

        input {
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
      }
    }
  }

  .detail-content {
    white-space: pre-wrap;
    word-break: break-word;
    line-height: 1.6;
    color: #1d1d1f;
  }

  // 弹窗样式已由全局样式统一处理，此处仅保留页面特定样式

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
}

// 响应式设计
@media (max-width: 1200px) {
  .notification-management {
    .page-header,
    .action-bar,
    .table-container {
      margin-left: 20px;
      margin-right: 20px;
    }
  }
}

@media (max-width: 768px) {
  .notification-management {
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
      gap: 16px;

      .search-section {
        width: 100%;
        flex-direction: column;
        gap: 12px;

        :deep(.ant-input-search),
        :deep(.ant-select) {
          width: 100% !important;
          margin-left: 0 !important;
        }
      }

      .button-section {
        width: 100%;
        flex-direction: column;

        .action-btn-primary,
        .action-btn-danger,
        .action-btn-secondary {
          width: 100%;
        }
      }
    }

    .table-container {
      margin: 0 16px 20px 16px;
      border-radius: 12px;
    }
  }
}
</style>
