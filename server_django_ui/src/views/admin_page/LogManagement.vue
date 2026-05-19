<template>
  <div class="log-management">
    <!-- 页面头部 - 苹果风格 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon-wrapper">
          <FileSearchOutlined class="header-icon" />
        </div>
        <div class="header-text">
          <h1 class="page-title">日志管理</h1>
          <p class="page-description">管理系统操作日志和审计记录</p>
        </div>
      </div>
    </div>

    <!-- 操作栏 - 苹果风格 -->
    <div class="action-bar">
      <a-form layout="inline" @submit.prevent class="search-form">
        <a-form-item label="ID">
          <a-input-number
            v-model:value="filters.id"
            :min="1"
            placeholder="日志ID"
            style="width: 140px"
            @pressEnter="onSearch"
          />
        </a-form-item>
        <a-form-item label="操作类型">
          <a-input
            v-model:value="filters.operation_type"
            placeholder="如 CREATE/UPDATE"
            allow-clear
            style="width: 180px"
            @pressEnter="onSearch"
          />
        </a-form-item>
        <a-form-item label="分类">
          <a-select
            v-model:value="filters.operation_module"
            allow-clear
            show-search
            placeholder="全部"
            style="width: 180px"
          >
            <a-select-option v-for="m in moduleOptions" :key="m" :value="m">{{
              m
            }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="请求方法">
          <a-select
            v-model:value="filters.request_method"
            allow-clear
            placeholder="全部"
            style="width: 140px"
          >
            <a-select-option value="GET">GET</a-select-option>
            <a-select-option value="POST">POST</a-select-option>
            <a-select-option value="PUT">PUT</a-select-option>
            <a-select-option value="DELETE">DELETE</a-select-option>
            <a-select-option value="PATCH">PATCH</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="请求路径">
          <a-input
            v-model:value="filters.request_path"
            placeholder="如 /api/user/list/"
            allow-clear
            style="width: 220px"
            @pressEnter="onSearch"
          />
        </a-form-item>
        <a-form-item label="时间范围">
          <a-range-picker v-model:value="dateRange" style="width: 260px" />
        </a-form-item>
        <a-form-item label="IP地址">
          <a-input
            v-model:value="filters.ip_address"
            placeholder="如 127.0.0.1"
            allow-clear
            style="width: 160px"
            @pressEnter="onSearch"
          />
        </a-form-item>
        <a-form-item label="状态码">
          <a-select
            v-model:value="filters.status"
            allow-clear
            placeholder="全部"
            style="width: 140px"
          >
            <a-select-option :value="200">200</a-select-option>
            <a-select-option :value="201">201</a-select-option>
            <a-select-option :value="400">400</a-select-option>
            <a-select-option :value="401">401</a-select-option>
            <a-select-option :value="403">403</a-select-option>
            <a-select-option :value="404">404</a-select-option>
            <a-select-option :value="500">500</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="关键字">
          <a-input
            v-model:value="filters.keyword"
            placeholder="描述/模块/路径关键字"
            allow-clear
            style="width: 220px"
            @pressEnter="onSearch"
          />
        </a-form-item>
        <a-form-item>
          <a-space wrap>
            <a-button
              type="primary"
              :loading="loading"
              @click="onSearch"
              class="action-btn-primary"
            >
              <template #icon><SearchOutlined /></template>
              查询
            </a-button>
            <a-button @click="onReset" class="action-btn-secondary">
              <template #icon><ClearOutlined /></template>
              重置
            </a-button>
            <a-button @click="onRefresh" class="action-btn-secondary">
              <template #icon><ReloadOutlined /></template>
              刷新
            </a-button>
            <a-button @click="exportCsv" class="action-btn-secondary">
              <template #icon><DownloadOutlined /></template>
              导出 CSV
            </a-button>
            <a-switch
              v-model:checked="errorOnly"
              checked-children="只看异常"
              un-checked-children="全部"
            />
            <a-switch
              v-model:checked="autoRefresh"
              checked-children="自动刷新"
              un-checked-children="手动刷新"
            />
          </a-space>
        </a-form-item>
      </a-form>
    </div>

    <!-- 统计卡片 - 苹果风格 -->
    <div class="stats-container">
      <a-space wrap>
        <a-tag color="green" class="stat-tag">2xx 成功: {{ statusStats.success }}</a-tag>
        <a-tag color="orange" class="stat-tag">4xx 客户端异常: {{ statusStats.clientError }}</a-tag>
        <a-tag color="red" class="stat-tag">5xx 服务异常: {{ statusStats.serverError }}</a-tag>
        <a-tag class="stat-tag">总数: {{ total }}</a-tag>
      </a-space>
    </div>

    <!-- 表格容器 - 苹果风格 -->
    <div class="table-container">
      <a-table
        :data-source="tableData"
        :columns="columns"
        :loading="loading"
        :pagination="pagination"
        :scroll="{ x: 1200 }"
        row-key="id"
        :rowClassName="rowClassName"
        @change="onTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'user'">
            <span>{{ record.user?.username || '-' }}</span>
          </template>
          <template v-else-if="column.dataIndex === 'response_status'">
            <a-tag :color="getStatusColor(record.response_status)">{{
              record.response_status
            }}</a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'is_success'">
            <a-tag
              :color="
                record.is_success === true
                  ? 'green'
                  : record.is_success === false
                    ? 'red'
                    : 'default'
              "
            >
              {{ record.is_success === true ? '成功' : record.is_success === false ? '失败' : '-' }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'created_at'">
            <span>{{ formatDateTime(record.created_at) }}</span>
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-button type="link" @click="openDetail(record)">详情</a-button>
          </template>
        </template>
      </a-table>
    </div>

    <a-drawer
      v-model:visible="detailVisible"
      :visible="detailVisible"
      :width="720"
      title="日志详情"
      placement="right"
    >
      <a-spin :spinning="detailLoading">
        <a-descriptions bordered column="1">
          <a-descriptions-item label="ID">{{ detailData?.id }}</a-descriptions-item>
          <a-descriptions-item label="用户">{{
            detailData?.user?.username || '-'
          }}</a-descriptions-item>
          <a-descriptions-item label="操作类型">{{
            detailData?.operation_type
          }}</a-descriptions-item>
          <a-descriptions-item label="类型说明">{{
            detailData?.action_type_display || '-'
          }}</a-descriptions-item>
          <a-descriptions-item label="操作模块">{{
            detailData?.operation_module
          }}</a-descriptions-item>
          <a-descriptions-item label="操作描述">{{
            detailData?.operation_description
          }}</a-descriptions-item>
          <a-descriptions-item label="目标模型">{{
            detailData?.target_model || '-'
          }}</a-descriptions-item>
          <a-descriptions-item label="目标对象ID">{{
            detailData?.target_object_id || '-'
          }}</a-descriptions-item>
          <a-descriptions-item label="IP地址">{{
            detailData?.ip_address || '-'
          }}</a-descriptions-item>
          <a-descriptions-item label="User-Agent">
            <pre class="json-pre">{{ detailData?.user_agent || '-' }}</pre>
          </a-descriptions-item>
          <a-descriptions-item label="请求方法">{{
            detailData?.request_method
          }}</a-descriptions-item>
          <a-descriptions-item label="请求路径">{{ detailData?.request_path }}</a-descriptions-item>
          <a-descriptions-item label="请求数据">
            <pre class="json-pre">{{ formatJson(detailData?.request_data) }}</pre>
          </a-descriptions-item>
          <a-descriptions-item label="响应状态码">
            <a-tag :color="getStatusColor(detailData?.response_status)">{{
              detailData?.response_status
            }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="状态说明">{{
            detailData?.status_display || '-'
          }}</a-descriptions-item>
          <a-descriptions-item label="结果">{{
            detailData?.is_success === true
              ? '成功'
              : detailData?.is_success === false
                ? '失败'
                : '-'
          }}</a-descriptions-item>
          <a-descriptions-item label="响应数据">
            <pre class="json-pre">{{ formatJson(detailData?.response_data) }}</pre>
          </a-descriptions-item>
          <a-descriptions-item label="执行时间(ms)">{{
            detailData?.execution_time ?? '-'
          }}</a-descriptions-item>
          <a-descriptions-item label="创建时间">{{ detailData?.created_at }}</a-descriptions-item>
          <a-descriptions-item label="更新时间">{{
            detailData?.updated_at || '-'
          }}</a-descriptions-item>
        </a-descriptions>
      </a-spin>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import dayjs, { Dayjs } from 'dayjs';
import {
  logApi,
  type LogListParams,
  type OperationLogItem,
  type OperationLogDetail,
} from '@/api/log';
import { handleError } from '@/utils/error_handler';
import {
  FileSearchOutlined,
  SearchOutlined,
  ClearOutlined,
  ReloadOutlined,
  DownloadOutlined,
} from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';

// 查询条件
const filters = reactive<LogListParams & { id?: number }>({
  page: 1,
  page_size: 10,
  operation_type: undefined,
  operation_module: undefined,
  id: undefined,
  start_date: undefined,
  end_date: undefined,
  ip_address: undefined,
  status: undefined,
});

const dateRange = ref<[Dayjs, Dayjs] | null>(null);

// 列表与分页
const loading = ref(false);
const tableData = ref<OperationLogItem[]>([]);
const allLogs = ref<OperationLogItem[]>([]); // 存储所有日志数据（用于客户端筛选）
const moduleOptions = ref<string[]>([]);
const errorOnly = ref(false);
const autoRefresh = ref(false);
let refreshTimer: number | null = null;
let currentAbort: AbortController | null = null;
const statusStats = reactive({ success: 0, clientError: 0, serverError: 0 });
const total = ref(0);
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  pageSizeOptions: ['10', '20', '50', '100'],
});

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '用户', dataIndex: 'user', key: 'user', width: 140 },
  { title: '类型', dataIndex: 'operation_type', key: 'operation_type', width: 120 },
  { title: '类型说明', dataIndex: 'action_type_display', key: 'action_type_display', width: 120 },
  { title: '模块', dataIndex: 'operation_module', key: 'operation_module', width: 160 },
  { title: '方法', dataIndex: 'request_method', key: 'request_method', width: 100 },
  { title: '路径', dataIndex: 'request_path', key: 'request_path' },
  { title: 'IP', dataIndex: 'ip_address', key: 'ip_address', width: 140 },
  { title: '状态', dataIndex: 'response_status', key: 'response_status', width: 100 },
  { title: '状态说明', dataIndex: 'status_display', key: 'status_display', width: 120 },
  { title: '结果', dataIndex: 'is_success', key: 'is_success', width: 90 },
  { title: '耗时(ms)', dataIndex: 'execution_time', key: 'execution_time', width: 120 },
  { title: '时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  { title: '操作', key: 'actions', width: 100 },
];

// 详情抽屉
const detailVisible = ref(false);
const detailLoading = ref(false);
const detailData = ref<OperationLogDetail | null>(null);

function formatJson(obj: Record<string, any> | undefined | null) {
  if (!obj) return '-';
  try {
    return JSON.stringify(obj, null, 2);
  } catch (e) {
    return String(obj);
  }
}

function getStatusColor(status?: number) {
  if (!status) return 'default';
  if (status >= 500) return 'red';
  if (status >= 400) return 'orange';
  if (status >= 300) return 'blue';
  return 'green';
}

function formatDateTime(val?: string) {
  if (!val) return '-';
  const d = dayjs(val);
  return d.isValid() ? d.format('YYYY-MM-DD HH:mm:ss') : val;
}

async function fetchList() {
  loading.value = true;
  try {
    // 取消上一次请求，避免并发和数据闪烁
    if (currentAbort) currentAbort.abort();
    currentAbort = new AbortController();

    // 检查是否需要客户端筛选（关键字搜索、ID搜索或操作类型搜索）
    // 如果后端不支持某些筛选，需要前端处理
    const needsClientFilter =
      (filters.keyword && filters.keyword.trim()) ||
      (filters.id !== undefined && filters.id !== null) ||
      (filters.operation_type && filters.operation_type.trim());

    // 组装并清理查询参数，避免传递 undefined/空字符串导致后端异常
    const raw: LogListParams & { id?: number } = { ...filters };
    raw.page = needsClientFilter ? 1 : pagination.current || 1;
    // 使用更合理的page_size，避免超出后端限制
    // 对于需要客户端筛选的情况，使用适中的page_size（50条）
    if (needsClientFilter) {
      // 所有客户端筛选都使用50条，避免超出后端限制
      raw.page_size = 50;
    } else {
      raw.page_size = pagination.pageSize || 10;
    }

    // 移除客户端筛选参数（后端可能不支持）
    const keyword = raw.keyword;
    const filterId = raw.id;
    const filterOperationType = raw.operation_type; // 保存操作类型用于客户端筛选
    // 先尝试后端查询，如果后端不支持，会在客户端筛选
    // 暂时保留 operation_type，让后端先尝试处理

    if (dateRange.value && dateRange.value.length === 2) {
      // 兼容后端多种命名与边界：日期和精确到秒的时间
      const startDate = dayjs(dateRange.value[0]).startOf('day');
      const endDate = dayjs(dateRange.value[1]).endOf('day');
      raw.start_date = startDate.format('YYYY-MM-DD');
      raw.end_date = endDate.format('YYYY-MM-DD');
    } else {
      raw.start_date = undefined;
      raw.end_date = undefined;
    }

    const params: Record<string, any> = {};
    Object.entries(raw).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        params[k] = v;
      }
    });
    // 追加时间范围的兼容字段（不影响未知后端，已知后端会使用其中之一）
    if (dateRange.value && dateRange.value.length === 2) {
      const startDate = dayjs(dateRange.value[0]).startOf('day');
      const endDate = dayjs(dateRange.value[1]).endOf('day');
      const startDt = startDate.format('YYYY-MM-DD HH:mm:ss');
      const endDt = endDate.format('YYYY-MM-DD HH:mm:ss');
      params.start_datetime = startDt;
      params.end_datetime = endDt;
      params.start_time = startDt;
      params.end_time = endDt;
      params.created_at__gte = startDt;
      params.created_at__lte = endDt;
      params.created_start = startDt;
      params.created_end = endDt;
      params.create_time_start = startDt;
      params.create_time_end = endDt;
    }

    let res: any;
    try {
      res = await logApi.getList(params as LogListParams, { signal: currentAbort.signal });
    } catch (error: any) {
      // 如果请求失败（如422错误），尝试降级处理
      if (error?.response?.status === 422 || error?.status === 422) {
        console.warn('后端返回422错误，可能是page_size过大，尝试使用较小的page_size');
        // 如果是因为page_size太大，尝试使用默认的page_size
        if (needsClientFilter && params.page_size > 50) {
          params.page_size = 50;
          try {
            res = await logApi.getList(params as LogListParams, { signal: currentAbort.signal });
          } catch (retryError) {
            console.error('重试后仍然失败:', retryError);
            throw retryError;
          }
        } else {
          throw error;
        }
      } else {
        throw error;
      }
    }

    // 兼容多种返回结构：
    // A) { success, code, message, data: { count, results } }
    // B) { count, results }
    // C) { success, code, message, data: [] }
    // D) 纯数组 []
    const unwrap = (payload: any) => {
      if (!payload) return { count: 0, results: [] };
      const d = 'data' in payload ? payload.data : payload;
      // DRF 标准结构：{ count, next, previous, results }
      if (d && typeof d === 'object' && 'results' in d) {
        const count = d.count ?? d.total ?? d.total_count ?? d?.pagination?.total_count ?? 0;
        return { count: Number(count) || 0, results: d.results || [] };
      }
      // 其它常见结构：{ list, total } / { items, total } / { logs, total_count }
      if (d && typeof d === 'object') {
        const results = d.list || d.items || d.logs || d.data;
        const count =
          d.count ?? d.total ?? d.total_count ?? d?.pagination?.total ?? d?.pagination?.total_count;
        if (Array.isArray(results)) {
          return { count: Number(count) || 0, results };
        }
      }
      // 纯数组（仅返回当前页数据，无法获知总数）
      if (Array.isArray(d)) {
        // 不将总数设为当前页长度，避免误判只有一页
        // 保持总数为 0，由分页组件根据请求后的 total 更新
        return { count: 0, results: d };
      }
      return { count: Number(d?.count ?? d?.total ?? d?.total_count ?? 0) || 0, results: [] };
    };

    const listData = unwrap(res);

    // 将后端原始字段映射为前端统一结构
    const normalizeItem = (it: any): OperationLogItem => {
      const id = it.id ?? it.log_id ?? it.pk ?? it._id ?? Math.random();
      const username = it.user?.username ?? it.username ?? it.user_name ?? '-';
      return {
        id,
        user: username ? { id: it.user?.id ?? it.user_id ?? 0, username } : null,
        operation_type: it.operation_type ?? it.action_type ?? it.type ?? '-',
        action_type_display: it.action_type_display ?? it.operation_type_display ?? it.type_display,
        operation_module: it.operation_module ?? it.module ?? it.category ?? '-',
        operation_description: it.operation_description ?? it.description ?? undefined,
        target_model: it.target_model ?? undefined,
        target_object_id: it.target_object_id ?? undefined,
        ip_address: it.ip_address ?? it.ip ?? undefined,
        request_method: it.request_method ?? it.method ?? '-',
        request_path: it.request_path ?? it.path ?? it.url ?? '-',
        response_status: it.response_status ?? it.status ?? 0,
        status_display: it.status_display ?? it.response_status_display ?? undefined,
        is_success:
          typeof it.is_success === 'boolean'
            ? it.is_success
            : typeof (it.response_status ?? it.status) === 'number'
              ? (it.response_status ?? it.status) < 400
              : undefined,
        execution_time: it.execution_time ?? it.duration_ms ?? undefined,
        created_at: it.created_at ?? it.create_time ?? it.created ?? '-',
      };
    };

    let allRows = (listData.results || []).map(normalizeItem);

    // 如果后端不支持关键字搜索或ID搜索，在前端进行客户端筛选
    if (needsClientFilter) {
      // 对于ID查询，如果第一次没找到且还有更多数据，尝试获取更多
      if (filterId !== undefined && filterId !== null) {
        const found = allRows.find((log: OperationLogItem) => log.id === filterId);
        // 如果没找到且返回的数据量等于page_size，说明可能还有更多数据
        if (!found && allRows.length === raw.page_size && listData.count > allRows.length) {
          console.log('ID查询未找到，尝试获取更多数据...');
          // 尝试获取更多页的数据（最多获取5页）
          let allFetchedRows = [...allRows];
          let currentPage = 2;
          const maxPages = 5;

          while (currentPage <= maxPages && allFetchedRows.length < listData.count) {
            try {
              const moreParams = { ...params };
              moreParams.page = currentPage;
              moreParams.page_size = raw.page_size;

              const moreRes = await logApi.getList(moreParams as LogListParams, {
                signal: currentAbort.signal,
              });
              const moreListData = unwrap(moreRes);
              const moreRows = (moreListData.results || []).map(normalizeItem);

              if (moreRows.length === 0) break;

              allFetchedRows = [...allFetchedRows, ...moreRows];

              // 检查是否找到了目标ID
              const foundInMore = allFetchedRows.find(
                (log: OperationLogItem) => log.id === filterId
              );
              if (foundInMore) {
                console.log(`✅ 在第${currentPage}页找到了目标ID`);
                break;
              }

              currentPage++;
            } catch (err) {
              console.warn(`获取第${currentPage}页数据失败:`, err);
              break;
            }
          }

          allRows = allFetchedRows;
        }
      }

      // 保存所有数据用于筛选
      allLogs.value = allRows;

      // 客户端ID筛选
      if (filterId !== undefined && filterId !== null) {
        allRows = allRows.filter((log: OperationLogItem) => {
          return log.id === filterId;
        });

        if (allRows.length === 0) {
          message.warning(`未找到ID为 ${filterId} 的日志记录`);
        }
      }

      // 客户端操作类型筛选
      if (filterOperationType && filterOperationType.trim()) {
        const operationTypeFilter = filterOperationType.trim().toUpperCase();
        allRows = allRows.filter((log: OperationLogItem) => {
          const logOperationType = (log.operation_type || '').toUpperCase();
          return (
            logOperationType === operationTypeFilter ||
            logOperationType.includes(operationTypeFilter)
          );
        });
      }

      // 客户端关键字搜索筛选
      if (keyword && keyword.trim()) {
        const keywordLower = keyword.trim().toLowerCase();
        allRows = allRows.filter((log: OperationLogItem) => {
          const description = (log.operation_description || '').toLowerCase();
          const module = (log.operation_module || '').toLowerCase();
          const path = (log.request_path || '').toLowerCase();
          const operationType = (log.operation_type || '').toLowerCase();
          const actionTypeDisplay = (log.action_type_display || '').toLowerCase();
          return (
            description.includes(keywordLower) ||
            module.includes(keywordLower) ||
            path.includes(keywordLower) ||
            operationType.includes(keywordLower) ||
            actionTypeDisplay.includes(keywordLower)
          );
        });
      }

      // 客户端分页
      const startIndex = (pagination.current - 1) * pagination.pageSize;
      const endIndex = startIndex + pagination.pageSize;
      const paginatedList = allRows.slice(startIndex, endIndex);

      tableData.value = errorOnly.value
        ? paginatedList.filter((r) => r.response_status >= 400)
        : paginatedList;
      total.value = allRows.length;
      pagination.total = allRows.length;

      console.log('✅ 客户端筛选后总数:', allRows.length, '条');
      console.log('✅ 当前页显示:', paginatedList.length, '条');
    } else {
      // 不需要客户端筛选，直接使用后端返回的数据
      tableData.value = errorOnly.value ? allRows.filter((r) => r.response_status >= 400) : allRows;
      allLogs.value = allRows;
    }

    // 统计状态分布（基于所有数据）
    statusStats.success = allRows.filter(
      (r) => r.response_status >= 200 && r.response_status < 300
    ).length;
    statusStats.clientError = allRows.filter(
      (r) => r.response_status >= 400 && r.response_status < 500
    ).length;
    statusStats.serverError = allRows.filter((r) => r.response_status >= 500).length;
    // 模块分类选项（去重）
    const set = new Set<string>();
    allRows.forEach((r) => r.operation_module && set.add(r.operation_module));
    moduleOptions.value = Array.from(set);

    // 当后端提供总数字段时使用之；若缺失则仅更新数据，不锁死分页为一页
    if (needsClientFilter && (keyword || filterId !== undefined || filterOperationType)) {
      // 客户端筛选时，总数已在上面的逻辑中设置
      // 不需要再次设置
    } else if (listData.count && Number(listData.count) > 0) {
      total.value = Number(listData.count);
      pagination.total = total.value;
    } else {
      // 后端未返回总数：为了允许翻页，按需放宽 total
      const pageLen = tableData.value.length;
      const size = pagination.pageSize || 10;
      if (pageLen >= size) {
        // 至少开放到下一页，随着翻页逐步扩展
        const minTotal = size * (pagination.current + 1);
        pagination.total = Math.max(pagination.total || 0, minTotal);
      } else {
        // 数据不足一页时，展示实际条数
        pagination.total = Math.max(pagination.total || 0, pageLen);
      }
    }
  } catch (error) {
    // 列表查询失败时，避免打断页面交互，清空数据并提示友好消息
    console.warn('日志列表获取失败:', error);
    tableData.value = [];
    total.value = 0;
    pagination.total = 0;
    // 使用轻提示替代全局错误弹窗
    import('ant-design-vue').then(({ message }) => {
      message.warning('日志列表加载失败，请稍后重试');
    });
  } finally {
    loading.value = false;
  }
}

function onSearch() {
  pagination.current = 1;
  fetchList();
}

function onReset() {
  filters.id = undefined;
  filters.operation_type = undefined;
  filters.operation_module = undefined;
  filters.request_method = undefined;
  filters.request_path = undefined;
  filters.keyword = undefined;
  filters.ip_address = undefined;
  filters.status = undefined;
  dateRange.value = null;
  pagination.current = 1;
  fetchList();
}

function onRefresh() {
  fetchList();
}

function exportCsv() {
  const rows = tableData.value;
  const headers = [
    'ID',
    '用户',
    '类型',
    '类型说明',
    '模块',
    '方法',
    '路径',
    'IP',
    '状态',
    '状态说明',
    '结果',
    '耗时(ms)',
    '时间',
  ];
  const lines = [headers.join(',')];
  rows.forEach((r) => {
    const cols = [
      r.id,
      r.user?.username || '-',
      r.operation_type,
      r.action_type_display ?? '',
      r.operation_module,
      r.request_method,
      r.request_path,
      r.ip_address || '-',
      r.response_status,
      r.status_display ?? '',
      r.is_success === true ? '成功' : r.is_success === false ? '失败' : '-',
      r.execution_time ?? '',
      formatDateTime(r.created_at),
    ];
    // 简单CSV转义
    lines.push(
      cols
        .map((v) => {
          const s = String(v ?? '');
          return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}` + '"' : s;
        })
        .join(',')
    );
  });
  const csvContent = '\ufeff' + lines.join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `operation-logs-${dayjs().format('YYYYMMDD-HHmmss')}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function onTableChange(pag: any) {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;

  // 检查是否需要客户端筛选
  const needsClientFilter =
    (filters.keyword && filters.keyword.trim()) ||
    (filters.id !== undefined && filters.id !== null) ||
    (filters.operation_type && filters.operation_type.trim());

  if (needsClientFilter && allLogs.value.length > 0) {
    // 如果有客户端筛选，直接在前端进行分页
    let processedList = [...allLogs.value];

    // 客户端ID筛选
    if (filters.id !== undefined && filters.id !== null) {
      processedList = processedList.filter((log: OperationLogItem) => {
        return log.id === filters.id;
      });
    }

    // 客户端操作类型筛选
    if (filters.operation_type && filters.operation_type.trim()) {
      const operationTypeFilter = filters.operation_type.trim().toUpperCase();
      processedList = processedList.filter((log: OperationLogItem) => {
        const logOperationType = (log.operation_type || '').toUpperCase();
        return (
          logOperationType === operationTypeFilter || logOperationType.includes(operationTypeFilter)
        );
      });
    }

    // 客户端关键字搜索筛选
    if (filters.keyword && filters.keyword.trim()) {
      const keywordLower = filters.keyword.trim().toLowerCase();
      processedList = processedList.filter((log: OperationLogItem) => {
        const description = (log.operation_description || '').toLowerCase();
        const module = (log.operation_module || '').toLowerCase();
        const path = (log.request_path || '').toLowerCase();
        const operationType = (log.operation_type || '').toLowerCase();
        const actionTypeDisplay = (log.action_type_display || '').toLowerCase();
        return (
          description.includes(keywordLower) ||
          module.includes(keywordLower) ||
          path.includes(keywordLower) ||
          operationType.includes(keywordLower) ||
          actionTypeDisplay.includes(keywordLower)
        );
      });
    }

    // 客户端分页
    const startIndex = (pag.current - 1) * pag.pageSize;
    const endIndex = startIndex + pag.pageSize;
    const paginatedList = processedList.slice(startIndex, endIndex);

    tableData.value = errorOnly.value
      ? paginatedList.filter((r) => r.response_status >= 400)
      : paginatedList;
    total.value = processedList.length;
    pagination.total = processedList.length;
  } else {
    // 不需要客户端筛选，重新获取数据
    fetchList();
  }
}

async function openDetail(record: OperationLogItem) {
  detailVisible.value = true;
  detailLoading.value = true;
  detailData.value = null;
  try {
    const id = Number(record.id);
    let res: any;
    // 优先使用路径参数形式
    try {
      res = await logApi.getDetail(id);
    } catch (e1) {
      // 回退到查询参数形式（兼容后端实现为 /api/log/detail/?id=xx 或 ?log_id=xx）
      res = await logApi.getDetailByQuery(id);
    }

    // 兼容包装与非包装返回
    const d = res && (res as any).data ? (res as any).data : (res as any);
    const item: any = d?.detail ?? d?.result ?? d?.item ?? d;
    // 保持已有展示字段尽可能填充
    detailData.value = {
      id: item.id ?? item.log_id ?? record.id,
      user:
        item.user ?? (record.user ? { id: record.user.id, username: record.user.username } : null),
      operation_type: item.operation_type ?? item.action_type ?? record.operation_type,
      action_type_display:
        item.action_type_display ?? item.operation_type_display ?? record.action_type_display,
      operation_module: item.operation_module ?? item.module ?? record.operation_module,
      operation_description:
        item.operation_description ?? item.description ?? record.operation_description ?? '-',
      target_model: item.target_model ?? undefined,
      target_object_id: item.target_object_id ?? undefined,
      ip_address: item.ip_address ?? item.ip ?? record.ip_address,
      user_agent: item.user_agent ?? item.ua ?? undefined,
      request_method: item.request_method ?? item.method ?? record.request_method,
      request_path: item.request_path ?? item.path ?? item.url ?? record.request_path,
      request_data: item.request_data ?? item.req_data ?? undefined,
      response_status: item.response_status ?? item.status ?? record.response_status,
      status_display: item.status_display ?? item.response_status_display ?? record.status_display,
      is_success:
        typeof item.is_success === 'boolean'
          ? item.is_success
          : typeof (item.response_status ?? item.status) === 'number'
            ? (item.response_status ?? item.status) < 400
            : record.is_success,
      response_data: item.response_data ?? item.res_data ?? undefined,
      execution_time: item.execution_time ?? item.duration_ms ?? record.execution_time,
      created_at: item.created_at ?? item.create_time ?? record.created_at,
      updated_at: item.updated_at ?? item.update_time ?? undefined,
    } as any;
  } catch (err) {
    handleError(err);
  } finally {
    detailLoading.value = false;
  }
}

onMounted(() => {
  fetchList();
  // 自动刷新控制
  watch(
    autoRefresh,
    (val) => {
      if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
      }
      if (val) {
        refreshTimer = window.setInterval(() => {
          fetchList();
        }, 10000);
      }
    },
    { immediate: false }
  );

  // 只看异常切换时重新滤数据
  watch(errorOnly, () => {
    // 不重新请求，基于当前数据客户端过滤
    const sourceData =
      allLogs.value.length > 0 && filters.keyword && filters.keyword.trim()
        ? allLogs.value
        : tableData.value;
    tableData.value = errorOnly.value
      ? sourceData.filter((r) => r.response_status >= 400)
      : sourceData;
  });
});

// 行样式：异常高亮
function rowClassName(record: OperationLogItem) {
  if (record.response_status >= 500) return 'row-critical';
  if (record.response_status >= 400) return 'row-error';
  return '';
}
</script>

<style scoped lang="scss">
.log-management {
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
        background: rgba(48, 207, 208, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

        &:hover {
          transform: scale(1.05);
          background: rgba(48, 207, 208, 0.15);
        }

        .header-icon {
          font-size: 24px;
          color: #30cfd0;
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

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      border-color: rgba(0, 0, 0, 0.12);
    }

    .search-form {
      width: 100%;

      :deep(.ant-form-item) {
        margin-bottom: 12px;
      }

      :deep(.ant-form-item-label > label) {
        font-weight: 500;
        color: #1d1d1f;
        font-size: 13px;
      }

      :deep(.ant-input-affix-wrapper),
      :deep(.ant-input-number),
      :deep(.ant-select-selector),
      :deep(.ant-picker) {
        border-radius: 8px;
        border: 0.5px solid rgba(0, 0, 0, 0.12);
        background: rgba(255, 255, 255, 0.8);
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

        &:hover {
          border-color: #3b82f6;
        }

        &:focus,
        &.ant-picker-focused {
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
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
    }
  }

  // 统计卡片 - 苹果风格
  .stats-container {
    margin: 0 28px 24px 28px;
    padding: 16px 24px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-radius: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 0.5px solid rgba(0, 0, 0, 0.08);
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      border-color: rgba(0, 0, 0, 0.12);
    }

    .stat-tag {
      border-radius: 8px;
      font-weight: 500;
      padding: 4px 12px;
      font-size: 13px;
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
        padding: 16px;
        font-size: 13px;
        letter-spacing: -0.1px;
      }

      .ant-table-tbody > tr {
        transition: all 0.2s ease;

        &:hover > td {
          background: rgba(0, 0, 0, 0.02);
        }

        > td {
          padding: 16px;
          border-bottom: 0.5px solid rgba(0, 0, 0, 0.06);
          color: #1d1d1f;
        }
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

  .row-error td {
    background-color: rgba(255, 247, 230, 0.5) !important;
  }

  .row-critical td {
    background-color: rgba(255, 241, 240, 0.5) !important;
  }

  .json-pre {
    white-space: pre-wrap;
    word-break: break-all;
    background: rgba(0, 0, 0, 0.02);
    border: 0.5px solid rgba(0, 0, 0, 0.08);
    padding: 12px;
    border-radius: 8px;
    font-size: 12px;
    color: #1d1d1f;
    max-height: 300px;
    overflow-y: auto;
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
}

// 响应式设计
@media (max-width: 1200px) {
  .log-management {
    .page-header,
    .action-bar,
    .stats-container,
    .table-container {
      margin-left: 20px;
      margin-right: 20px;
    }
  }
}

@media (max-width: 768px) {
  .log-management {
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

      .search-form {
        :deep(.ant-form-item) {
          width: 100%;
          margin-bottom: 12px;
        }
      }
    }

    .stats-container,
    .table-container {
      margin: 0 16px 20px 16px;
      border-radius: 12px;
    }
  }
}
</style>
