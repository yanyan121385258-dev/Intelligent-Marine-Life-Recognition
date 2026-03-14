<template>
  <div class="model-management">
    <div class="page-header">
      <h2 class="page-title">
        <RobotOutlined class="title-icon" />
        模型管理
      </h2>
      <p class="page-description">管理YOLO检测模型的上传、配置和启用状态</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="action-left">
        <a-button type="primary" @click="showUploadModal">
          <template #icon>
            <UploadOutlined />
          </template>
          上传模型
        </a-button>
        <a-button @click="refreshModels">
          <template #icon>
            <ReloadOutlined />
          </template>
          刷新
        </a-button>
      </div>
      <div class="action-right">
        <a-input-search
          v-model:value="searchKeyword"
          placeholder="搜索模型名称或版本"
          style="width: 300px"
          @search="handleSearch"
        />
      </div>
    </div>

    <!-- 模型列表 -->
    <a-table
      :columns="columns"
      :data-source="filteredModels"
      :loading="loading"
      :pagination="pagination"
      row-key="id"
      class="model-table"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'name'">
          <div class="model-name">
            <RobotOutlined class="model-icon" />
            <div class="model-info">
              <div class="name">{{ record.name }}</div>
              <div class="version">v{{ record.version }}</div>
            </div>
          </div>
        </template>

        <template v-if="column.key === 'status'">
          <a-tag :color="record.is_enabled ? 'green' : 'default'">
            {{ record.is_enabled ? '已启用' : '未启用' }}
          </a-tag>
        </template>

        <template v-if="column.key === 'categories'">
          <div class="categories">
            <a-tag
              v-for="category in Object.keys(record.categories || {})"
              :key="category"
              color="blue"
            >
              {{ category }}
            </a-tag>
          </div>
        </template>

        <template v-if="column.key === 'created_at'">
          {{ formatDate(record.created_at) }}
        </template>

        <template v-if="column.key === 'actions'">
          <div class="action-buttons">
            <a-button size="small" @click="viewModel(record)">
              <template #icon>
                <EyeOutlined />
              </template>
              查看
            </a-button>
            <a-button
              size="small"
              :type="record.is_enabled ? 'default' : 'primary'"
              @click="toggleModelStatus(record)"
            >
              <template #icon>
                <PoweroffOutlined />
              </template>
              {{ record.is_enabled ? '禁用' : '启用' }}
            </a-button>
            <a-button size="small" @click="editModel(record)">
              <template #icon>
                <EditOutlined />
              </template>
              编辑
            </a-button>
            <a-popconfirm title="确定要删除这个模型吗？" @confirm="deleteModel(record)">
              <a-button size="small" danger>
                <template #icon>
                  <DeleteOutlined />
                </template>
                删除
              </a-button>
            </a-popconfirm>
          </div>
        </template>
      </template>
    </a-table>

    <!-- 上传模型弹窗 -->
    <a-modal
      v-model:visible="uploadModalVisible"
      title="上传模型"
      :confirm-loading="uploading"
      @ok="handleUpload"
      @cancel="handleUploadCancel"
      width="600px"
    >
      <a-form ref="uploadFormRef" :model="uploadForm" :rules="uploadRules" layout="vertical">
        <a-form-item label="模型文件" name="zip_file">
          <input
            ref="folderInputRef"
            type="file"
            webkitdirectory
            directory
            multiple
            style="display: none"
            @change="handleFolderSelect"
          />
          <input
            ref="zipInputRef"
            type="file"
            accept=".zip"
            style="display: none"
            @change="handleZipSelect"
          />
          <div
            ref="draggerContainerRef"
            class="custom-dragger"
            :class="{ 'drag-active': isDraggingOver }"
            @click="handleDraggerClick"
            @dragover.prevent="handleDragOver"
            @dragenter.prevent="handleDragOver"
            @dragleave.prevent="handleDragLeave"
            @drop.prevent="handleDrop"
            :style="{
              border: isDraggingOver ? '4px solid #3b82f6' : '3px dashed rgba(0, 0, 0, 0.12)',
              borderRadius: '20px',
              background: isDraggingOver ? 'rgba(255, 255, 255, 1)' : 'rgba(255, 255, 255, 0.9)',
              padding: '60px 40px',
              cursor: 'pointer',
              minHeight: '280px',
              margin: '16px 0',
              boxShadow: isDraggingOver
                ? '0 0 0 8px rgba(59, 130, 246, 0.15), 0 12px 32px rgba(59, 130, 246, 0.3)'
                : '0 1px 3px rgba(0, 0, 0, 0.1)',
              transform: isDraggingOver ? 'scale(1.02)' : 'scale(1)',
              transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
            }"
          >
            <div
              style="
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 16px;
                pointer-events: none;
              "
            >
              <div
                :style="{
                  fontSize: '72px',
                  color: isDraggingOver ? '#3b82f6' : '#6366f1',
                  lineHeight: '1',
                  transition: 'all 0.3s ease',
                }"
              >
                <InboxOutlined />
              </div>
              <div
                :style="{
                  fontSize: isDraggingOver ? '22px' : '20px',
                  fontWeight: '600',
                  color: isDraggingOver ? '#3b82f6' : '#1d1d1f',
                  margin: '0',
                  transition: 'all 0.3s ease',
                  letterSpacing: '-0.2px',
                }"
              >
                {{ isDraggingOver ? '松开鼠标以上传' : '点击或拖拽文件到此区域' }}
              </div>
              <div style="fontsize: 15px; color: #86868b; margin: 0">
                支持上传
                <span
                  style="
                    color: #3b82f6;
                    fontweight: 600;
                    padding: 2px 8px;
                    background: rgba(59, 130, 246, 0.1);
                    borderradius: 6px;
                    margin: 0 2px;
                  "
                  >文件夹</span
                >
                或
                <span
                  style="
                    color: #3b82f6;
                    fontweight: 600;
                    padding: 2px 8px;
                    background: rgba(59, 130, 246, 0.1);
                    borderradius: 6px;
                    margin: 0 2px;
                  "
                  >ZIP压缩包</span
                >
              </div>
              <div style="fontsize: 13px; color: #86868b; margin: 0">
                选择文件夹将自动打包为ZIP后上传
              </div>
              <div
                v-if="fileList.length > 0"
                style="
                  margin-top: 12px;
                  padding: 12px 24px;
                  background: rgba(59, 130, 246, 0.1);
                  backdrop-filter: saturate(180%) blur(20px);
                  -webkit-backdrop-filter: saturate(180%) blur(20px);
                  border-radius: 12px;
                  color: #3b82f6;
                  font-size: 16px;
                  font-weight: 600;
                  display: flex;
                  align-items: center;
                  gap: 8px;
                  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
                  border: 0.5px solid rgba(59, 130, 246, 0.2);
                "
              >
                <CheckCircleOutlined />
                <span>已选择 {{ fileList.length }} 个文件</span>
              </div>
            </div>
          </div>

          <!-- 上传方式弹窗 -->
          <a-modal
            v-model:visible="draggerMenuVisible"
            title="选择上传方式"
            :footer="null"
            :centered="true"
            width="460px"
          >
            <div class="upload-choice-modal">
              <div
                class="choice-grid"
                style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px"
              >
                <div
                  class="choice-card folder"
                  role="button"
                  tabindex="0"
                  @click="pickFolder"
                  @keyup.enter="pickFolder"
                  style="
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    padding: 18px 14px;
                    text-align: center;
                    cursor: pointer;
                    background: linear-gradient(180deg, #fff 0%, #fafafa 100%);
                    transition: all 0.2s ease;
                  "
                  onmouseover="
                    this.style.boxShadow = '0 8px 22px rgba(59,130,246,.18)';
                    this.style.borderColor = '#3b82f6';
                  "
                  onmouseout="
                    this.style.boxShadow = '';
                    this.style.borderColor = '#e5e7eb';
                  "
                >
                  <div
                    class="icon"
                    aria-hidden="true"
                    style="font-size: 28px; line-height: 1; margin-bottom: 8px; color: #10b981"
                  >
                    <FolderOpenOutlined />
                  </div>
                  <div class="title" style="font-size: 16px; font-weight: 700; color: #111827">
                    选择文件夹
                  </div>
                  <div class="desc" style="margin-top: 6px; font-size: 12px; color: #6b7280">
                    自动打包为 ZIP 后上传
                  </div>
                </div>
                <div
                  class="choice-card zip"
                  role="button"
                  tabindex="0"
                  @click="pickZip"
                  @keyup.enter="pickZip"
                  style="
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    padding: 18px 14px;
                    text-align: center;
                    cursor: pointer;
                    background: linear-gradient(180deg, #fff 0%, #fafafa 100%);
                    transition: all 0.2s ease;
                  "
                  onmouseover="
                    this.style.boxShadow = '0 8px 22px rgba(59,130,246,.18)';
                    this.style.borderColor = '#3b82f6';
                  "
                  onmouseout="
                    this.style.boxShadow = '';
                    this.style.borderColor = '#e5e7eb';
                  "
                >
                  <div
                    class="icon"
                    aria-hidden="true"
                    style="font-size: 28px; line-height: 1; margin-bottom: 8px; color: #3b82f6"
                  >
                    <FileZipOutlined />
                  </div>
                  <div class="title" style="font-size: 16px; font-weight: 700; color: #111827">
                    选择 ZIP 文件
                  </div>
                  <div class="desc" style="margin-top: 6px; font-size: 12px; color: #6b7280">
                    直接上传压缩包
                  </div>
                </div>
              </div>
              <div
                class="choice-divider"
                style="text-align: center; color: #9ca3af; font-size: 12px; margin-top: 8px"
              >
                或
              </div>
              <div class="tips" style="text-align: center; color: #64748b; font-size: 12px">
                也可以将 ZIP 或整个文件夹直接拖拽到上方区域
              </div>
            </div>
          </a-modal>
        </a-form-item>

        <a-form-item label="模型名称" name="name">
          <a-input v-model:value="uploadForm.name" placeholder="请输入模型名称" />
        </a-form-item>

        <a-form-item label="模型版本" name="version">
          <a-input v-model:value="uploadForm.version" placeholder="请输入模型版本，如：yolov11" />
        </a-form-item>

        <a-form-item label="模型描述" name="description">
          <a-textarea
            v-model:value="uploadForm.description"
            placeholder="请输入模型描述"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 模型详情弹窗 -->
    <a-modal
      v-model:visible="detailModalVisible"
      title="模型详情"
      :footer="null"
      width="800px"
      :destroy-on-close="true"
    >
      <div v-if="currentModel" class="model-detail">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="模型名称">
            {{ currentModel.name }}
          </a-descriptions-item>
          <a-descriptions-item label="模型版本">
            {{ currentModel.version }}
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="currentModel.is_enabled ? 'green' : 'default'">
              {{ currentModel.is_enabled ? '已启用' : '未启用' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">
            {{ formatDate(currentModel.created_at) }}
          </a-descriptions-item>
          <a-descriptions-item label="模型文件" :span="2">
            {{ currentModel.model_file }}
          </a-descriptions-item>
          <a-descriptions-item label="模型路径" :span="2">
            {{ currentModel.model_path }}
          </a-descriptions-item>
          <a-descriptions-item label="权重路径" :span="2">
            {{ currentModel.weights_folder_path }}
          </a-descriptions-item>
          <a-descriptions-item label="检测类别" :span="2">
            <div class="categories">
              <a-tag
                v-for="category in Object.keys(currentModel.categories)"
                :key="category"
                color="blue"
              >
                {{ category }}
              </a-tag>
            </div>
          </a-descriptions-item>
          <a-descriptions-item label="模型描述" :span="2">
            {{ currentModel.description || '暂无描述' }}
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-modal>

    <!-- 编辑模型弹窗 -->
    <a-modal
      v-model:visible="editModalVisible"
      title="编辑模型"
      :confirm-loading="editing"
      @ok="handleEdit"
      @cancel="handleEditCancel"
      width="500px"
    >
      <a-form ref="editFormRef" :model="editForm" :rules="editRules" layout="vertical">
        <a-form-item label="模型名称" name="name">
          <a-input v-model:value="editForm.name" placeholder="请输入模型名称" />
        </a-form-item>

        <a-form-item label="模型版本" name="version">
          <a-input v-model:value="editForm.version" placeholder="请输入模型版本" />
        </a-form-item>

        <a-form-item label="模型描述" name="description">
          <a-textarea v-model:value="editForm.description" placeholder="请输入模型描述" :rows="3" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { message } from 'ant-design-vue';
import {
  RobotOutlined,
  UploadOutlined,
  ReloadOutlined,
  EyeOutlined,
  PoweroffOutlined,
  EditOutlined,
  DeleteOutlined,
  InboxOutlined,
  FolderOpenOutlined,
  FileZipOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons-vue';
import { yoloApi, type YoloModel } from '@/api/yolo';
import JSZip from 'jszip';

// 响应式数据
const loading = ref(false);
const uploading = ref(false);
const editing = ref(false);
const models = ref<YoloModel[]>([]);
const searchKeyword = ref('');

// 弹窗状态
const uploadModalVisible = ref(false);
const detailModalVisible = ref(false);
const editModalVisible = ref(false);
const currentModel = ref<YoloModel | null>(null);

// 文件上传
const fileList = ref([]);
const folderInputRef = ref<HTMLInputElement>();
const zipInputRef = ref<HTMLInputElement>();
const draggerMenuVisible = ref(false);
const draggerContainerRef = ref<HTMLDivElement>();
const isDraggingOver = ref(false);

// 表单数据
const uploadForm = reactive({
  name: '',
  version: '',
  description: '',
});

const editForm = reactive({
  name: '',
  version: '',
  description: '',
});

// 表单引用
const uploadFormRef = ref();
const editFormRef = ref();

// 表单验证规则
const uploadRules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  version: [{ required: true, message: '请输入模型版本', trigger: 'blur' }],
};

const editRules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  version: [{ required: true, message: '请输入模型版本', trigger: 'blur' }],
};

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条记录`,
});

// 表格列配置
const columns = [
  {
    title: '模型信息',
    key: 'name',
    width: 200,
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
  },
  {
    title: '检测类别',
    key: 'categories',
    width: 200,
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 150,
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
  },
];

// 过滤后的模型列表
const filteredModels = computed(() => {
  if (!searchKeyword.value) {
    return models.value;
  }
  return models.value.filter(
    (model) =>
      model.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      model.version.toLowerCase().includes(searchKeyword.value.toLowerCase())
  );
});

// 格式化日期
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString();
};

// 选择文件夹
const selectFolder = () => {
  folderInputRef.value?.click();
};

// 选择ZIP文件
const selectZipFile = () => {
  zipInputRef.value?.click();
};

// 处理文件夹选择
const handleFolderSelect = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files.length > 0) {
    // 将FileList转换为数组并构造为upload组件需要的格式，保存路径信息
    const files = Array.from(input.files).map((file, index) => {
      // 获取文件的相对路径
      const relativePath = (file as any).webkitRelativePath || file.name;

      // 将路径信息附加到文件对象上
      const fileWithPath = Object.defineProperty(file, '_relativePath', {
        value: relativePath,
        writable: true,
        enumerable: false,
        configurable: true,
      });

      return {
        uid: `folder-${index}`,
        name: file.name,
        status: 'done',
        originFileObj: fileWithPath,
        _relativePath: relativePath,
      };
    });
    fileList.value = files as any;
    console.log('📁 选择了文件夹，包含文件数:', files.length);

    const hasPt = files.some((f) => /\.pt$/i.test(f.name));
    if (!hasPt) {
      message.warning('未检测到 .pt 权重文件，请确认文件夹内容');
    } else {
      message.success(`已选择文件夹，共 ${files.length} 个文件`);
    }
  }
};

// 拖拽区域点击：弹出选择器菜单（优先用按钮触发原生input）
const handleDraggerClick = () => {
  // 切换显示弹出菜单
  draggerMenuVisible.value = true;
};

// 菜单动作
const pickFolder = () => {
  draggerMenuVisible.value = false;
  selectFolder();
};

const pickZip = () => {
  draggerMenuVisible.value = false;
  selectZipFile();
};

// 处理ZIP文件选择
const handleZipSelect = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files.length > 0) {
    const file = input.files[0];
    fileList.value = [
      {
        uid: 'zip-file',
        name: file.name,
        status: 'done',
        originFileObj: file,
      },
    ] as any;
    console.log('📦 选择了ZIP文件:', file.name);
  }
};

// 拖拽进入时样式反馈
const handleDragOver = (e: DragEvent) => {
  e.preventDefault();
  e.stopPropagation();
  isDraggingOver.value = true;
  console.log('🎯 拖拽进入区域');
};

// 拖拽离开
const handleDragLeave = (e: DragEvent) => {
  e.preventDefault();
  isDraggingOver.value = false;
  console.log('🎯 拖拽离开区域');
};

// 使用 DataTransferItemList 判断拖入类型（文件夹/ZIP）
const handleDrop = async (e: DragEvent) => {
  console.log('🎯 Drop 事件触发');
  try {
    e.preventDefault();
    e.stopPropagation();
    // 清空由 a-upload 内部可能添加的临时列表
    fileList.value = [];
    isDraggingOver.value = false;

    console.log('📦 检查 dataTransfer:', e.dataTransfer);
    console.log('📦 dataTransfer.items:', e.dataTransfer?.items);
    console.log('📦 dataTransfer.files:', e.dataTransfer?.files);

    const items = e.dataTransfer?.items || (e as any).dataTransfer?.items;
    if (!items || items.length === 0) {
      console.warn('⚠️ 没有找到 items');
      return;
    }

    console.log('📦 找到 items 数量:', items.length);
    const filesWithPath: Array<{ file: File; path: string }> = [];

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      console.log(`📦 处理 item ${i}:`, item.kind, item.type);

      if (item.kind === 'file') {
        // 优先使用 File System Access API（更稳定识别目录）
        if ((item as any).getAsFileSystemHandle) {
          console.log('🔧 尝试使用 File System Access API');
          try {
            const handle = await (item as any).getAsFileSystemHandle();
            console.log('🔧 Handle 类型:', handle.kind, handle.name);

            // 如果是文件，直接获取
            if (handle.kind === 'file') {
              const file = await handle.getFile();
              console.log('📄 直接获取文件:', file.name, file.size);
              filesWithPath.push({ file, path: file.name });
            } else {
              // 如果是目录，递归遍历
              const collected = await collectFromFSHandle(handle);
              console.log('✅ 从 FSHandle 收集到文件:', collected.length);
              filesWithPath.push(...collected);
            }
            continue;
          } catch (err) {
            console.warn('⚠️ File System Access API 失败:', err);
          }
        }

        // 退回到 webkitGetAsEntry
        console.log('🔧 尝试使用 webkitGetAsEntry');
        try {
          const entry = (item as any).webkitGetAsEntry ? (item as any).webkitGetAsEntry() : null;
          console.log('🔧 Entry:', entry, 'isDirectory:', entry?.isDirectory);

          if (entry && entry.isDirectory) {
            console.log('📁 检测到文件夹，开始读取...');
            const dirFiles = await readAllFilesFromDirectory(entry);
            console.log('✅ 从文件夹读取到文件:', dirFiles.length);
            filesWithPath.push(...dirFiles);
          } else {
            const file = item.getAsFile();
            console.log('📄 获取单个文件:', file?.name);
            if (file) filesWithPath.push({ file, path: file.name });
          }
        } catch (err) {
          console.warn('⚠️ webkitGetAsEntry 失败:', err);
          const file = item.getAsFile();
          if (file) {
            console.log('📄 兜底获取文件:', file.name);
            filesWithPath.push({ file, path: file.name });
          }
        }
      }
    }

    // 兜底：某些环境 items 不可用，改用 dataTransfer.files
    if (filesWithPath.length === 0 && e.dataTransfer?.files?.length) {
      console.log('🔧 使用 dataTransfer.files 兜底');
      for (let i = 0; i < e.dataTransfer.files.length; i++) {
        const f = e.dataTransfer.files.item(i);
        if (f) {
          console.log('📄 从 files 获取:', f.name);
          filesWithPath.push({ file: f, path: f.name });
        }
      }
    }

    console.log('📦 最终收集到的文件数:', filesWithPath.length);
    if (filesWithPath.length === 0) {
      console.warn('⚠️ 没有收集到任何文件');
      message.warning('未识别到文件，请重试');
      return;
    }

    const isSingleZip =
      filesWithPath.length === 1 && /\.zip$/i.test(filesWithPath[0].file.name || '');
    console.log('📦 是否为单个ZIP:', isSingleZip);

    if (isSingleZip) {
      fileList.value = [
        {
          uid: 'zip-file',
          name: filesWithPath[0].file.name || 'archive.zip',
          status: 'done',
          originFileObj: filesWithPath[0].file,
        },
      ] as any;
      console.log('✅ 已选择ZIP文件:', filesWithPath[0].file.name);
      message.success('已选择ZIP文件: ' + filesWithPath[0].file.name);
      return;
    }

    // 为每个文件保存路径信息，用于后续压缩
    fileList.value = filesWithPath.map((item, idx) => {
      // 创建一个带路径信息的文件对象
      const fileWithPath = Object.defineProperty(item.file, '_relativePath', {
        value: item.path,
        writable: true,
        enumerable: false,
        configurable: true,
      });

      return {
        uid: `drop-${idx}`,
        name: item.file.name,
        status: 'done',
        originFileObj: fileWithPath,
        _relativePath: item.path, // 同时在外层也保存一份
      };
    }) as any;

    const hasPt = filesWithPath.some((item) => /\.pt$/i.test(item.file.name));
    console.log('📦 是否包含.pt文件:', hasPt);

    if (!hasPt) {
      message.warning('未检测到 .pt 权重文件，请确认文件夹内容');
    }
    console.log('✅ 已选择文件夹，共', filesWithPath.length, '个文件');
    message.success(`已选择文件夹，共 ${filesWithPath.length} 个文件`);
  } catch (err) {
    console.error('❌ 处理拖拽文件失败:', err);
    message.error('处理文件失败: ' + err);
  }
};

// 使用 File System Access API 递归采集文件（返回带路径信息的对象）
const collectFromFSHandle = async (
  handle: any,
  parent = ''
): Promise<Array<{ file: File; path: string }>> => {
  const out: Array<{ file: File; path: string }> = [];
  try {
    console.log('🔧 collectFromFSHandle 收到 handle:', handle.kind, handle.name);

    if (handle.kind === 'file') {
      console.log('📄 正在获取文件...');
      const file = await handle.getFile();
      const filePath = parent ? `${parent}${file.name}` : file.name;
      console.log('✅ 获取到文件:', file.name, file.size, '路径:', filePath);
      out.push({ file, path: filePath });
      console.log('📊 当前 out 数组:', out.length);
    } else if (handle.kind === 'directory') {
      console.log('📁 正在遍历目录...');
      const newParent = parent + (handle.name ? `${handle.name}/` : '');
      // @ts-ignore: for-await supported in Chromium
      for await (const entry of handle.values()) {
        const child = await collectFromFSHandle(entry, newParent);
        out.push(...child);
      }
      console.log('✅ 目录遍历完成，文件数:', out.length);
    }
  } catch (err) {
    console.error('❌ collectFromFSHandle 错误:', err);
  }
  console.log('📊 collectFromFSHandle 返回值:', out.length);
  return out;
};

// 递归读取目录内所有文件（返回带路径信息的对象）
const readAllFilesFromDirectory = (
  entry: any,
  parentPath = ''
): Promise<Array<{ file: File; path: string }>> => {
  return new Promise((resolve) => {
    const files: Array<{ file: File; path: string }> = [];
    const reader = entry.createReader();
    const readEntries = () => {
      reader.readEntries(async (entries: any[]) => {
        if (entries.length === 0) {
          resolve(files);
          return;
        }
        for (const e of entries) {
          if (e.isFile) {
            await new Promise<void>((res) => {
              e.file((file: File) => {
                try {
                  const base = parentPath || (entry.fullPath || '').replace(/^\//, '');
                  const filePath = base ? `${base}/${file.name}` : file.name;
                  files.push({ file, path: filePath });
                } catch (err) {
                  // 如果出错，使用文件名作为路径
                  files.push({ file, path: file.name });
                }
                res();
              });
            });
          } else if (e.isDirectory) {
            const dirPath = parentPath ? `${parentPath}/${e.name}` : e.name;
            const subFiles = await readAllFilesFromDirectory(e, dirPath);
            files.push(...subFiles);
          }
        }
        // 继续读取下一批条目直到为空
        readEntries();
      });
    };
    readEntries();
  });
};

// 上传前处理：仅阻止自动上传，不在此阶段校验类型
const beforeUpload = (file: any) => {
  const isZip = file?.type === 'application/zip' || /\.zip$/i.test(file?.name || '');
  if (isZip && file.size) {
    const isLt100M = file.size / 1024 / 1024 < 100;
    if (!isLt100M) {
      message.error('文件大小不能超过100MB!');
      return false;
    }
  }
  return false;
};

// 获取模型列表
const fetchModels = async () => {
  try {
    loading.value = true;
    console.log('🔍 开始获取模型列表...');

    const response = await yoloApi.getModels();
    console.log('📋 模型列表API响应:', response);

    if (response.success && response.data) {
      models.value = response.data;
      pagination.total = response.data.length;
      console.log('✅ 模型列表获取成功:', models.value);
    } else {
      console.error('❌ 获取模型列表失败:', response.message);
      message.error(response.message || '获取模型列表失败');
    }
  } catch (error) {
    console.error('❌ 获取模型列表异常:', error);
    message.error('获取模型列表失败，请检查网络连接');
  } finally {
    loading.value = false;
  }
};

// 刷新模型列表
const refreshModels = () => {
  fetchModels();
};

// 显示上传弹窗
const showUploadModal = () => {
  uploadModalVisible.value = true;
  // 重置表单
  Object.assign(uploadForm, {
    name: '',
    version: '',
    description: '',
  });
  fileList.value = [];
};

// 压缩文件夹为ZIP
const compressFolderToZip = async (files: any[]): Promise<File> => {
  const zip = new JSZip();

  // 遍历所有文件，使用保存的路径信息
  for (const file of files) {
    const src = file.originFileObj || file;
    // 尝试多种方式获取路径信息
    const relative =
      file._relativePath ||
      (src as any)._relativePath ||
      (src as any).webkitRelativePath ||
      src.name;
    if (src) {
      const filePath = relative;
      const fileData = await src.arrayBuffer();
      zip.file(filePath, fileData);
      console.log('📦 添加文件到ZIP:', filePath);
    }
  }

  // 生成ZIP文件
  const zipBlob = await zip.generateAsync({ type: 'blob' });
  const zipFile = new File([zipBlob], `${uploadForm.name || 'model'}.zip`, {
    type: 'application/zip',
  });

  return zipFile;
};

// 处理上传
const handleUpload = async () => {
  try {
    await uploadFormRef.value.validate();

    if (fileList.value.length === 0) {
      message.error('请选择要上传的模型文件或文件夹');
      return;
    }

    uploading.value = true;

    let finalFile: File;

    // 检查是否是文件夹（多个文件 或 有路径信息）
    const isFolder =
      fileList.value.length > 1 ||
      fileList.value.some(
        (f: any) =>
          f._relativePath || f.originFileObj?._relativePath || f.originFileObj?.webkitRelativePath
      );

    // 如果只有一个文件，检查是否是ZIP
    const isSingleZip = fileList.value.length === 1 && /\.zip$/i.test(fileList.value[0].name);

    if (isFolder && !isSingleZip) {
      // 文件夹：压缩为ZIP
      console.log('📦 检测到文件夹，开始压缩...');
      finalFile = await compressFolderToZip(fileList.value);
      console.log('✅ 文件夹压缩完成:', finalFile.name, finalFile.size);
    } else {
      // ZIP文件：直接使用
      finalFile = fileList.value[0].originFileObj;
      console.log('📁 使用ZIP文件:', finalFile.name);
    }

    const formData = new FormData();
    formData.append('zip_file', finalFile);
    formData.append('name', uploadForm.name);
    formData.append('version', uploadForm.version);
    formData.append('description', uploadForm.description);

    console.log('🔍 开始上传模型:', {
      name: uploadForm.name,
      version: uploadForm.version,
      description: uploadForm.description,
      fileName: finalFile.name,
      fileSize: finalFile.size,
    });

    const response = await yoloApi.uploadModel(formData);
    console.log('📋 模型上传API响应:', response);

    if (response.success) {
      message.success('模型上传成功');
      uploadModalVisible.value = false;
      fetchModels();
    } else {
      console.error('❌ 模型上传失败:', response.message);
      message.error(response.message || '模型上传失败');
    }
  } catch (error) {
    console.error('❌ 模型上传异常:', error);
    message.error('模型上传失败');
  } finally {
    uploading.value = false;
  }
};

// 取消上传
const handleUploadCancel = () => {
  uploadModalVisible.value = false;
  fileList.value = [];
};

// 查看模型详情
const viewModel = async (model: YoloModel) => {
  try {
    console.log('🔍 开始获取模型详情:', model.id);

    const response = await yoloApi.getModelDetail(model.id);
    console.log('📋 模型详情API响应:', response);

    if (response.success && response.data) {
      currentModel.value = response.data;
      detailModalVisible.value = true;
      console.log('✅ 模型详情获取成功:', currentModel.value);
      console.log('🔍 弹窗状态:', detailModalVisible.value);
      console.log('🔍 当前模型数据:', currentModel.value);
    } else {
      console.error('❌ 获取模型详情失败:', response.message);
      message.error(response.message || '获取模型详情失败');
    }
  } catch (error) {
    console.error('❌ 获取模型详情异常:', error);
    message.error('获取模型详情失败');
  }
};

// 切换模型状态
const toggleModelStatus = async (model: YoloModel) => {
  try {
    console.log('🔍 切换模型状态:', model.id, '当前状态:', model.is_enabled);

    const response = await yoloApi.enableModel(model.id);
    console.log('📋 模型状态切换API响应:', response);

    if (response.success) {
      message.success(model.is_enabled ? '模型已禁用' : '模型已启用');
      fetchModels();
    } else {
      console.error('❌ 模型状态切换失败:', response.message);
      message.error(response.message || '操作失败');
    }
  } catch (error) {
    console.error('❌ 模型状态切换异常:', error);
    message.error('操作失败');
  }
};

// 编辑模型
const editModel = (model: YoloModel) => {
  currentModel.value = model;
  Object.assign(editForm, {
    name: model.name,
    version: model.version,
    description: model.description || '',
  });
  editModalVisible.value = true;
};

// 处理编辑
const handleEdit = async () => {
  try {
    await editFormRef.value.validate();

    if (!currentModel.value) return;

    editing.value = true;

    const response = await yoloApi.updateModel(currentModel.value.id, {
      name: editForm.name,
      version: editForm.version,
    });

    if (response.success) {
      message.success('模型信息更新成功');
      editModalVisible.value = false;
      fetchModels();
    } else {
      message.error(response.message || '更新失败');
    }
  } catch (error) {
    console.error('更新失败:', error);
    message.error('更新失败');
  } finally {
    editing.value = false;
  }
};

// 取消编辑
const handleEditCancel = () => {
  editModalVisible.value = false;
};

// 删除模型
const deleteModel = async (model: YoloModel) => {
  try {
    const response = await yoloApi.deleteModel(model.id);
    if (response.success) {
      message.success('模型删除成功');
      fetchModels();
    } else {
      message.error(response.message || '删除失败');
    }
  } catch (error) {
    console.error('删除失败:', error);
    message.error('删除失败');
  }
};

// 搜索处理
const handleSearch = () => {
  // 搜索逻辑已在computed中处理
  // 重置分页到第一页
  pagination.current = 1;
};

// 组件挂载时获取数据
onMounted(() => {
  fetchModels();
  // 兜底：直接给真实DOM绑定原生事件，避免三方组件吞掉拖拽事件
  const el = draggerContainerRef.value;
  if (el) {
    el.addEventListener('dragover', (e) => {
      e.preventDefault();
    });
    el.addEventListener('drop', (e) => {
      e.preventDefault();
      handleDrop(e as DragEvent);
    });
  }
  // 全局兜底（有些层级会拦截元素事件）
  const getInside = (ev: DragEvent) => {
    const r = draggerContainerRef.value?.getBoundingClientRect();
    if (!r) return false;
    const x = ev.clientX,
      y = ev.clientY;
    return x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
  };
  const dragOverHandler = (ev: DragEvent) => {
    ev.preventDefault();
    if (getInside(ev)) {
      isDraggingOver.value = true;
      if (ev.dataTransfer) ev.dataTransfer.dropEffect = 'copy';
    } else {
      isDraggingOver.value = false;
    }
  };
  const dropHandler = (ev: DragEvent) => {
    ev.preventDefault();
    if (getInside(ev)) {
      handleDrop(ev);
    }
    isDraggingOver.value = false;
  };
  window.addEventListener('dragover', dragOverHandler);
  window.addEventListener('drop', dropHandler);
});
</script>

<style scoped lang="scss">
.model-management {
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

    .page-title {
      display: flex;
      align-items: center;
      margin: 0 0 4px 0;
      font-size: 24px;
      font-weight: 600;
      color: #1d1d1f;
      letter-spacing: -0.3px;
      line-height: 1.2;

      .title-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: rgba(99, 102, 241, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        color: #6366f1;
        font-size: 24px;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

        &:hover {
          transform: scale(1.05);
          background: rgba(99, 102, 241, 0.15);
        }
      }
    }

    .page-description {
      margin: 0;
      color: #86868b;
      font-size: 14px;
      font-weight: 400;
      padding-left: 64px;
    }
  }

  :deep(.ant-upload-drag-container) {
    .dragger-actions {
      margin-top: 8px;
      display: flex;
      justify-content: center;
      gap: 8px;
    }
  }

  // 操作栏 - 苹果风格
  .action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 0 28px 24px 28px;
    padding: 20px 24px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-radius: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 0.5px solid rgba(0, 0, 0, 0.08);
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    flex-wrap: wrap;
    gap: 16px;

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      border-color: rgba(0, 0, 0, 0.12);
    }

    .action-left {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;

      .ant-btn {
        border-radius: 12px;
        height: 40px;
        padding: 0 20px;
        font-weight: 500;
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

        &.ant-btn-primary {
          &:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
          }

          &:active {
            transform: translateY(0);
          }
        }

        &:not(.ant-btn-primary) {
          border-color: rgba(0, 0, 0, 0.12);
          color: #1d1d1f;
          background: rgba(255, 255, 255, 0.8);

          &:hover {
            background: rgba(0, 0, 0, 0.04);
            border-color: rgba(0, 0, 0, 0.16);
            transform: translateY(-1px);
          }
        }
      }
    }

    .action-right {
      :deep(.ant-input-search) {
        .ant-input {
          border-radius: 10px;
          border: 0.5px solid rgba(0, 0, 0, 0.12);
          background: rgba(255, 255, 255, 0.8);
          transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
          height: 40px;

          &:hover {
            border-color: #3b82f6;
          }

          &:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }
        }

        .ant-btn {
          border-radius: 0 10px 10px 0;
          height: 40px;
        }
      }
    }
  }

  // 表格容器 - 苹果风格
  .model-table {
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

    .model-name {
      display: flex;
      align-items: center;

      .model-icon {
        font-size: 24px;
        color: #6366f1;
        margin-right: 12px;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 10px;
        transition: all 0.2s ease;
      }

      .model-info {
        .name {
          font-weight: 600;
          color: #1d1d1f;
          font-size: 15px;
          margin-bottom: 2px;
        }

        .version {
          font-size: 12px;
          color: #86868b;
          font-weight: 400;
        }
      }
    }

    .categories {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;

      .ant-tag {
        border-radius: 6px;
        font-weight: 500;
        padding: 2px 10px;
        border: 0.5px solid currentColor;
        opacity: 0.8;
      }
    }

    .action-buttons {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;

      .ant-btn {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);

        &:hover {
          transform: translateY(-1px);
        }
      }
    }
  }

  .model-detail {
    .categories {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;

      .ant-tag {
        border-radius: 6px;
        font-weight: 500;
        padding: 2px 10px;
        border: 0.5px solid currentColor;
        opacity: 0.8;
      }
    }
  }

  // 上传拖拽区域 - 苹果风格
  .custom-dragger {
    position: relative;
    border: 3px dashed rgba(0, 0, 0, 0.12);
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    padding: 60px 40px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    min-height: 280px;
    margin: 16px 0;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .custom-dragger::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
    border-radius: 20px;
    opacity: 0;
    z-index: -1;
    transition: opacity 0.3s ease;
  }

  .custom-dragger:hover {
    border-color: #3b82f6;
    background: rgba(255, 255, 255, 1);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.2);
  }

  .custom-dragger:hover::before {
    opacity: 0.05;
  }

  .dragger-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
    position: relative;
    z-index: 1;
  }

  .dragger-icon {
    font-size: 72px;
    color: #6366f1;
    line-height: 1;
    animation: float 3s ease-in-out infinite;
    transition: all 0.3s ease;
  }

  .custom-dragger:hover .dragger-icon {
    color: #3b82f6;
    transform: scale(1.1);
  }

  .dragger-title {
    font-size: 20px;
    font-weight: 600;
    color: #1d1d1f;
    margin: 0;
    transition: color 0.3s ease;
    letter-spacing: -0.2px;
  }

  .custom-dragger:hover .dragger-title {
    color: #3b82f6;
  }

  .dragger-desc {
    font-size: 15px;
    color: #86868b;
    margin: 0;
  }

  .dragger-desc .highlight {
    color: #3b82f6;
    font-weight: 600;
    padding: 2px 8px;
    background: rgba(59, 130, 246, 0.1);
    border-radius: 6px;
    margin: 0 2px;
  }

  .dragger-tips {
    font-size: 13px;
    color: #86868b;
    margin: 0;
  }

  .file-selected {
    margin-top: 12px;
    padding: 12px 24px;
    background: rgba(59, 130, 246, 0.1);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-radius: 12px;
    color: #3b82f6;
    font-size: 16px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    animation: slideIn 0.3s ease;
    border: 0.5px solid rgba(59, 130, 246, 0.2);
  }

  @keyframes float {
    0%,
    100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(-12px);
    }
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .custom-dragger.drag-active {
    border-color: #3b82f6;
    border-width: 4px;
    border-style: solid;
    background: rgba(255, 255, 255, 1);
    box-shadow:
      0 0 0 8px rgba(59, 130, 246, 0.15),
      0 12px 32px rgba(59, 130, 246, 0.3);
    transform: scale(1.02);
  }

  .custom-dragger.drag-active .dragger-icon {
    color: #3b82f6;
    transform: scale(1.2);
    animation: pulse 0.6s ease infinite;
  }

  .custom-dragger.drag-active .dragger-title {
    color: #3b82f6;
    font-size: 22px;
  }

  @keyframes pulse {
    0%,
    100% {
      transform: scale(1.2);
    }
    50% {
      transform: scale(1.3);
    }
  }

  .dragger-pop {
    margin-top: 8px;
    display: flex;
    justify-content: center;
    gap: 8px;
  }

  .upload-choice-modal {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    .choice-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }
    .choice-card {
      border: 0.5px solid rgba(0, 0, 0, 0.12);
      border-radius: 12px;
      padding: 20px 16px;
      text-align: center;
      cursor: pointer;
      transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      background: rgba(255, 255, 255, 0.8);
      backdrop-filter: saturate(180%) blur(20px);
      -webkit-backdrop-filter: saturate(180%) blur(20px);
    }
    .choice-card:hover {
      border-color: #3b82f6;
      box-shadow: 0 8px 22px rgba(59, 130, 246, 0.18);
      transform: translateY(-2px);
      background: rgba(255, 255, 255, 1);
    }
    .choice-card .icon {
      font-size: 28px;
      color: #3b82f6;
      margin-bottom: 8px;
      transition: all 0.25s ease;
    }
    .choice-card:hover .icon {
      transform: scale(1.1);
    }
    .choice-card .title {
      font-weight: 600;
      color: #1d1d1f;
      font-size: 16px;
      letter-spacing: -0.1px;
    }
    .choice-card .desc {
      margin-top: 6px;
      font-size: 12px;
      color: #86868b;
    }
    .choice-divider {
      text-align: center;
      color: #86868b;
      font-size: 12px;
    }
    .tips {
      margin-top: 2px;
      font-size: 12px;
      color: #86868b;
      text-align: center;
    }
  }

  /* 解决 Ant Modal Teleport 导致 scoped 样式不生效的问题 */
  :deep(.upload-choice-modal) {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  :deep(.upload-choice-modal .choice-grid) {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  :deep(.upload-choice-modal .choice-card) {
    border: 0.5px solid rgba(0, 0, 0, 0.12);
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
  }
  :deep(.upload-choice-modal .choice-card:hover) {
    border-color: #3b82f6;
    box-shadow: 0 8px 22px rgba(59, 130, 246, 0.18);
    transform: translateY(-2px);
    background: rgba(255, 255, 255, 1);
  }
  :deep(.upload-choice-modal .choice-card.folder:hover .icon) {
    color: #10b981;
    transform: scale(1.1);
  }
  :deep(.upload-choice-modal .choice-card.zip:hover .icon) {
    color: #3b82f6;
    transform: scale(1.1);
  }
  :deep(.upload-choice-modal .choice-card .icon) {
    font-size: 28px;
    line-height: 1;
    margin-bottom: 8px;
    color: #3b82f6;
    transition: all 0.25s ease;
  }
  :deep(.upload-choice-modal .choice-card .title) {
    font-size: 16px;
    font-weight: 600;
    color: #1d1d1f;
    letter-spacing: -0.1px;
  }
  :deep(.upload-choice-modal .choice-card .desc) {
    margin-top: 6px;
    font-size: 12px;
    color: #86868b;
  }
  :deep(.upload-choice-modal .choice-divider) {
    text-align: center;
    color: #86868b;
    font-size: 12px;
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

// 响应式设计
@media (max-width: 1200px) {
  .model-management {
    .page-header,
    .action-bar,
    .model-table {
      margin-left: 20px;
      margin-right: 20px;
    }
  }
}

@media (max-width: 768px) {
  .model-management {
    .page-header {
      padding: 24px 16px;

      .page-title {
        font-size: 20px;

        .title-icon {
          width: 40px;
          height: 40px;
          font-size: 20px;
          margin-right: 12px;
        }
      }

      .page-description {
        font-size: 13px;
        padding-left: 52px;
      }
    }

    .action-bar {
      margin: 0 16px 20px 16px;
      padding: 16px;
      flex-direction: column;
      align-items: stretch;

      .action-left {
        width: 100%;
        justify-content: flex-start;
      }

      .action-right {
        width: 100%;

        :deep(.ant-input-search) {
          width: 100% !important;
        }
      }
    }

    .model-table {
      margin: 0 16px 20px 16px;
      border-radius: 12px;
    }
  }
}

/* 确保弹窗正确显示 */
:deep(.ant-modal) {
  z-index: 1000 !important;
}

:deep(.ant-modal-mask) {
  z-index: 999 !important;
}

:deep(.ant-modal-wrap) {
  z-index: 1000 !important;
}
</style>
