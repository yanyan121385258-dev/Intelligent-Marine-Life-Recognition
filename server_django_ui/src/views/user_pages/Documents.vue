<template>
  <div class="documents-page">
    <a-card title="文档管理" class="documents-card">
      <template #extra>
        <a-space>
          <a-input-search
            v-model:value="searchText"
            placeholder="搜索文档"
            style="width: 200px"
            @search="handleSearch"
          />
          <a-button type="primary" @click="showUploadModal = true">
            <UploadOutlined />
            上传文档
          </a-button>
        </a-space>
      </template>

      <a-table
        :columns="columns"
        :data-source="filteredDocuments"
        :pagination="{ pageSize: 10 }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <a-space>
              <component :is="getFileIcon(record.type)" />
              <a @click="previewDocument(record)">{{ record.name }}</a>
            </a-space>
          </template>
          <template v-else-if="column.key === 'size'">
            {{ formatFileSize(record.size) }}
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="downloadDocument(record)">下载</a-button>
              <a-button type="link" size="small" @click="shareDocument(record)">分享</a-button>
              <a-button type="link" size="small" danger @click="deleteDocument(record.id)"
                >删除</a-button
              >
            </a-space>
          </template>
        </template>
      </a-table>

      <!-- 上传文档模态框 -->
      <a-modal
        v-model:open="showUploadModal"
        title="上传文档"
        @ok="handleUpload"
        @cancel="resetUploadForm"
      >
        <a-form :model="uploadForm" :label-col="{ span: 6 }" :wrapper-col="{ span: 18 }">
          <a-form-item label="文档名称" name="name">
            <a-input v-model:value="uploadForm.name" placeholder="可选，默认使用文件名" />
          </a-form-item>
          <a-form-item label="文档描述" name="description">
            <a-textarea v-model:value="uploadForm.description" :rows="3" />
          </a-form-item>
          <a-form-item
            label="选择文件"
            name="file"
            :rules="[{ required: true, message: '请选择文件' }]"
          >
            <a-upload
              v-model:file-list="fileList"
              :before-upload="beforeUpload"
              :remove="handleRemove"
              accept=".pdf,.doc,.docx,.txt,.md"
            >
              <a-button>
                <UploadOutlined />
                选择文件
              </a-button>
            </a-upload>
          </a-form-item>
        </a-form>
      </a-modal>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import {
  UploadOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileWordOutlined,
} from '@ant-design/icons-vue';

interface Document {
  id: number;
  name: string;
  description: string;
  type: string;
  size: number;
  created_at: string;
  updated_at: string;
}

const columns = [
  { title: '文档名称', dataIndex: 'name', key: 'name' },
  { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
  { title: '类型', dataIndex: 'type', key: 'type', width: 100 },
  { title: '大小', dataIndex: 'size', key: 'size', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 150 },
  { title: '操作', key: 'action', width: 200 },
];

const documents = ref<Document[]>([
  {
    id: 1,
    name: '项目需求文档.pdf',
    description: '项目的详细需求说明',
    type: 'pdf',
    size: 2048576,
    created_at: '2024-01-01',
    updated_at: '2024-01-01',
  },
  {
    id: 2,
    name: '技术方案.docx',
    description: '技术实现方案文档',
    type: 'docx',
    size: 1024000,
    created_at: '2024-01-02',
    updated_at: '2024-01-02',
  },
]);

const searchText = ref('');
const showUploadModal = ref(false);
const fileList = ref([]);
const uploadForm = ref({
  name: '',
  description: '',
});

const filteredDocuments = computed(() => {
  if (!searchText.value) {
    return documents.value;
  }
  return documents.value.filter(
    (doc) =>
      doc.name.toLowerCase().includes(searchText.value.toLowerCase()) ||
      doc.description.toLowerCase().includes(searchText.value.toLowerCase())
  );
});

const getFileIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    pdf: FilePdfOutlined,
    doc: FileWordOutlined,
    docx: FileWordOutlined,
    txt: FileTextOutlined,
    md: FileTextOutlined,
  };
  return iconMap[type] || FileTextOutlined;
};

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const handleSearch = () => {
  // 搜索逻辑已在 computed 中实现
};

const previewDocument = (doc: Document) => {
  message.info(`预览文档: ${doc.name}`);
  // 这里可以实现文档预览功能
};

const downloadDocument = (doc: Document) => {
  message.success(`开始下载: ${doc.name}`);
  // 这里可以实现文档下载功能
};

const shareDocument = (doc: Document) => {
  message.info(`分享文档: ${doc.name}`);
  // 这里可以实现文档分享功能
};

const deleteDocument = (id: number) => {
  const index = documents.value.findIndex((doc) => doc.id === id);
  if (index > -1) {
    documents.value.splice(index, 1);
    message.success('文档删除成功');
  }
};

const beforeUpload = (file: any) => {
  const isValidType = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'text/markdown',
  ].includes(file.type);
  if (!isValidType) {
    message.error('只能上传 PDF、Word、TXT、MD 格式的文件!');
    return false;
  }
  const isLt10M = file.size / 1024 / 1024 < 10;
  if (!isLt10M) {
    message.error('文件大小不能超过 10MB!');
    return false;
  }
  return false; // 阻止自动上传
};

const handleRemove = () => {
  fileList.value = [];
};

const handleUpload = () => {
  if (fileList.value.length === 0) {
    message.error('请选择文件');
    return;
  }

  const file = fileList.value[0] as any;
  const newDocument: Document = {
    id: Date.now(),
    name: uploadForm.value.name || file.name,
    description: uploadForm.value.description,
    type: file.name.split('.').pop() || 'unknown',
    size: file.size,
    created_at: new Date().toISOString().split('T')[0],
    updated_at: new Date().toISOString().split('T')[0],
  };

  documents.value.unshift(newDocument);
  message.success('文档上传成功');
  resetUploadForm();
};

const resetUploadForm = () => {
  showUploadModal.value = false;
  fileList.value = [];
  uploadForm.value = {
    name: '',
    description: '',
  };
};

onMounted(() => {
  // 这里可以调用获取文档列表的API
});
</script>

<style scoped lang="scss">
.documents-page {
  padding: 24px;

  .documents-card {
    :deep(.ant-table-tbody > tr > td) {
      vertical-align: top;
    }
  }
}
</style>
