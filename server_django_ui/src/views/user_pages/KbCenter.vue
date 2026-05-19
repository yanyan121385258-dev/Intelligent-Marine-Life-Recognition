<template>
  <div class="kb-center">
    <div class="page-header">
      <h1 class="page-title">
        <BookOutlined class="title-icon" />
        知识库中心
      </h1>
      <p class="page-description">统一管理知识条目、语义检索、智能问答与知识图谱</p>
    </div>

    <a-tabs v-model:activeKey="activeTab" class="kb-tabs">
      <a-tab-pane key="items" tab="知识条目">
        <div class="tab-section">
          <div class="items-search-row">
            <a-input-search
              v-model:value="itemsQuery"
              placeholder="搜索知识条目标题..."
              enter-button
              size="large"
              @search="handleItemsSearch"
            />
          </div>

          <div class="items-toolbar">
            <a-button type="primary" @click="openItemModal"> 新建知识条目 </a-button>
          </div>

          <div class="stats-row">
            <a-row :gutter="16">
              <a-col :xs="24" :sm="12" :md="6">
                <div class="stat-card">
                  <div class="stat-label">条目总数</div>
                  <div class="stat-value">{{ itemsTotal }}</div>
                </div>
              </a-col>
              <a-col :xs="24" :sm="12" :md="6">
                <div class="stat-card">
                  <div class="stat-label">当前页文本条目</div>
                  <div class="stat-value">{{ textItemsCount }}</div>
                </div>
              </a-col>
              <a-col :xs="24" :sm="12" :md="6">
                <div class="stat-card">
                  <div class="stat-label">当前页代码条目</div>
                  <div class="stat-value">{{ codeItemsCount }}</div>
                </div>
              </a-col>
              <a-col :xs="24" :sm="12" :md="6">
                <div class="stat-card">
                  <div class="stat-label">当前页片段总数</div>
                  <div class="stat-value">{{ currentPageChunkCount }}</div>
                </div>
              </a-col>
            </a-row>
          </div>

          <a-spin :spinning="itemsLoading">
            <div v-if="items.length" class="items-grid">
              <div v-for="item in items" :key="item.id" class="item-card">
                <div class="item-header">
                  <div class="item-title">{{ item.title }}</div>
                  <div class="item-tags">
                    <a-tag>{{ item.modality || 'unknown' }}</a-tag>
                    <a-tag>{{ item.source_type || 'unknown' }}</a-tag>
                  </div>
                </div>
                <div class="item-meta">
                  <div class="meta-row">
                    <span class="meta-label">片段数</span>
                    <span class="meta-value">{{ item.chunk_count ?? '-' }}</span>
                  </div>
                  <div class="meta-row">
                    <span class="meta-label">创建时间</span>
                    <span class="meta-value">{{ formatDate(item.created_at) }}</span>
                  </div>
                  <div class="meta-row">
                    <span class="meta-label">更新时间</span>
                    <span class="meta-value">{{ formatDate(item.updated_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <a-empty v-else description="暂无知识条目" class="tab-empty" />

            <div v-if="itemsTotal > 0" class="pagination-wrapper">
              <a-pagination
                v-model:current="itemsPage.current"
                v-model:page-size="itemsPage.pageSize"
                :total="itemsTotal"
                :show-size-changer="true"
                :show-quick-jumper="true"
                :show-total="(total) => `共 ${total} 条`"
                @change="handleItemsPageChange"
              />
            </div>
          </a-spin>
        </div>
      </a-tab-pane>

      <a-tab-pane key="qa" tab="智能问答">
        <div class="tab-section qa-panel">
          <!-- Header Card -->
          <div class="qa-header-card">
            <div class="qa-header-main">
              <div class="qa-header-text">
                <div class="qa-header-title-row">
                  <BookOutlined class="qa-header-icon" />
                  <h2 class="qa-header-title">智能问答 (RAG)</h2>
                </div>
                <p class="qa-header-desc">
                  基于知识库内容的智能问答系统，自动检索相关知识并生成准确回答
                </p>
              </div>
              <div class="qa-header-controls">
                <span class="qa-header-label">检索上下文数量：</span>
                <a-select v-model:value="qaK" size="small" class="qa-header-select">
                  <a-select-option :value="3">3</a-select-option>
                  <a-select-option :value="5">5</a-select-option>
                  <a-select-option :value="10">10</a-select-option>
                </a-select>
              </div>
            </div>
          </div>

          <!-- Chat Container -->
          <div class="qa-chat-card">
            <!-- Messages Scroll Area -->
            <div class="qa-messages" ref="qaMessagesRef">
              <template v-for="msg in qaMessages" :key="msg.id">
                <!-- 用户问题气泡 -->
                <div v-if="msg.type === 'question'" class="qa-message-row qa-message-row-question">
                  <div class="qa-bubble qa-bubble-question">
                    <div class="qa-bubble-header qa-bubble-header-question">
                      <span class="qa-bubble-label">提问</span>
                    </div>
                    <div class="qa-bubble-content">{{ msg.content }}</div>
                  </div>
                </div>

                <!-- AI 回答气泡 -->
                <div v-else-if="msg.type === 'answer'" class="qa-message-row qa-message-row-answer">
                  <div class="qa-bubble qa-bubble-answer">
                    <div class="qa-bubble-header qa-bubble-header-answer">
                      <span class="qa-bubble-label">AI 回答</span>
                    </div>
                    <div class="qa-bubble-content">{{ msg.content }}</div>

                    <!-- 参考来源 -->
                    <div v-if="msg.sources && msg.sources.length" class="qa-sources">
                      <div class="qa-sources-header">
                        <span class="qa-sources-title">参考来源 ({{ msg.sources.length }})</span>
                      </div>
                      <div class="qa-source-list">
                        <div v-for="(src, idx) in msg.sources" :key="idx" class="qa-source-card">
                          <div class="qa-source-title">{{ src.item_title || '未命名条目' }}</div>
                          <div class="qa-source-meta">
                            条目 ID: {{ src.item_id ?? '-' }} | 片段 ID: {{ src.chunk_id ?? '-' }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 加载状态气泡 -->
                <div
                  v-else-if="msg.type === 'loading'"
                  class="qa-message-row qa-message-row-answer"
                >
                  <div class="qa-bubble qa-bubble-answer qa-bubble-loading">
                    <div class="qa-loading">
                      <span class="qa-loading-spinner"></span>
                      <span class="qa-loading-text">正在思考...</span>
                    </div>
                  </div>
                </div>
              </template>

              <div v-if="!qaMessages.length && !qaLoading" class="qa-empty-state">
                <p>在下方输入你的问题，系统会基于知识库内容进行回答。</p>
              </div>
            </div>

            <!-- Input Area -->
            <div class="qa-input-area">
              <a-textarea
                v-model:value="qaQuestion"
                class="qa-input"
                :rows="2"
                placeholder="请输入你的问题，Enter 发送，Shift+Enter 换行"
                @pressEnter="handleQaPressEnter"
              />
              <a-button
                type="primary"
                :loading="qaLoading"
                :disabled="!qaQuestion.trim()"
                @click="handleQaSubmit"
              >
                发送
              </a-button>
            </div>
          </div>
        </div>
      </a-tab-pane>

      <a-tab-pane key="graph" tab="知识图谱">
        <div class="graph-container">
          <!-- 顶部 Header -->
          <div class="graph-header-row">
            <div class="header-left">
              <h3 class="section-title"><DeploymentUnitOutlined /> 知识图谱</h3>
              <span class="section-desc"
                >实体和关系的可视化展示，支持自动抽取和手动管理 | 🖱️ 可拖拽节点</span
              >
            </div>
            <div class="header-right">
              <a-button type="primary" class="add-entity-btn" @click="openEntityModal('create')">
                <PlusOutlined /> 添加实体
              </a-button>
            </div>
          </div>

          <!-- 统计卡片行 -->
          <div class="stats-grid-row">
            <div class="stat-info-card">
              <div class="stat-title">实体总数</div>
              <div class="stat-num">{{ entitiesTotal }}</div>
            </div>
            <div class="stat-info-card">
              <div class="stat-title">关系总数</div>
              <div class="stat-num">{{ relationsTotal }}</div>
            </div>
            <div class="stat-info-card">
              <div class="stat-title">实体类型</div>
              <div class="stat-num">{{ entityTypesCount }}</div>
            </div>
            <div class="stat-info-card">
              <div class="stat-title">关系类型</div>
              <div class="stat-num">{{ relationTypesCount }}</div>
            </div>
          </div>

          <!-- 中间主要内容：图谱画布 + 详情面板 -->
          <div class="graph-main-content">
            <!-- 左侧画布 -->
            <div class="graph-canvas-card">
              <div class="card-header">
                <span class="card-title">图谱可视化</span>
                <div class="card-actions">
                  <a-button size="small" type="link" @click="fetchGraph">刷新</a-button>
                </div>
              </div>
              <div class="canvas-wrapper" ref="canvasWrapperRef">
                <canvas
                  ref="graphCanvasRef"
                  @mousedown="handleCanvasMouseDown"
                  @mousemove="handleCanvasMouseMove"
                  @mouseup="handleCanvasMouseUp"
                  @mouseleave="handleCanvasMouseLeave"
                ></canvas>
                <div class="canvas-overlay-tip" v-if="entities.length === 0">
                  <a-empty description="暂无图谱数据，请添加实体或进行自动抽取" />
                </div>
              </div>
              <div class="canvas-footer">
                <span class="footer-tip"
                  >🖱️ 拖拽节点可移动 | 点击节点查看详情 | {{ entities.length }} 个实体,
                  {{ relations.length }} 个关系</span
                >
              </div>
            </div>

            <!-- 右侧详情 -->
            <div class="entity-detail-panel">
              <div class="card-header">
                <span class="card-title">实体详情</span>
              </div>
              <div class="detail-content" v-if="selectedEntity">
                <div class="detail-group">
                  <div class="label">名称</div>
                  <div class="value-lg">{{ selectedEntity.name }}</div>
                </div>

                <div class="detail-group">
                  <div class="label">类型</div>
                  <div class="value">
                    <a-tag color="blue">{{ selectedEntity.type || 'Unknown' }}</a-tag>
                  </div>
                </div>

                <div class="detail-group" v-if="selectedEntity.properties">
                  <div class="label">属性</div>
                  <div class="props-list">
                    <div
                      v-for="(val, key) in typeof selectedEntity.properties === 'string'
                        ? JSON.parse(selectedEntity.properties)
                        : selectedEntity.properties"
                      :key="key"
                      class="prop-item"
                    >
                      <span class="prop-key">{{ key }}:</span>
                      <span class="prop-val">{{ val }}</span>
                    </div>
                  </div>
                </div>

                <div class="detail-group">
                  <div class="label">关联关系</div>
                  <div class="relations-list">
                    <div v-if="selectedEntityRelations.length === 0" class="no-rel">暂无关联</div>
                    <div
                      v-else
                      v-for="rel in selectedEntityRelations"
                      :key="rel.id"
                      class="rel-item"
                    >
                      <LinkOutlined />
                      <span class="rel-type">{{ rel.relation_type }}</span>
                      <ArrowRightOutlined class="arrow" />
                      <span class="rel-target">
                        {{
                          rel.target === selectedEntity.id
                            ? getEntityName(rel.source)
                            : getEntityName(rel.target)
                        }}
                      </span>
                    </div>
                  </div>
                </div>

                <div class="detail-actions">
                  <a-button block @click="openEntityModal('edit', selectedEntity)">
                    <EditOutlined /> 编辑
                  </a-button>
                  <a-popconfirm
                    title="确定删除该实体？"
                    @confirm="handleDeleteEntity(selectedEntity.id)"
                  >
                    <a-button block danger> <DeleteOutlined /> 删除 </a-button>
                  </a-popconfirm>
                </div>
              </div>
              <div class="detail-empty" v-else>
                <div class="empty-state">
                  <NodeIndexOutlined class="empty-icon" />
                  <p>请在图谱中点击选择一个节点</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 底部实体列表 -->
          <div class="entity-list-card">
            <div class="card-header">
              <span class="card-title">实体列表</span>
            </div>
            <a-table
              :data-source="entities"
              :columns="entityTableColumns"
              :pagination="{ pageSize: 5 }"
              row-key="id"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'type'">
                  <a-tag color="blue">{{ record.type }}</a-tag>
                </template>
                <template v-if="column.key === 'relationCount'">
                  {{ getEntityRelationCount(record.id) }}
                </template>
                <template v-if="column.key === 'actions'">
                  <a-button type="text" size="small" @click="openEntityModal('edit', record)">
                    <EditOutlined />
                  </a-button>
                </template>
              </template>
            </a-table>
          </div>

          <!-- 自动抽取模块 (保留在底部或折叠) -->
          <div class="extract-card">
            <div class="card-header">
              <span class="card-title">自动抽取</span>
            </div>
            <div class="extract-body">
              <a-input-group compact>
                <a-input
                  v-model:value="extractText"
                  style="width: calc(100% - 200px)"
                  placeholder="输入文本自动抽取..."
                />
                <a-button type="primary" :loading="extractLoading" @click="handleExtractFromText"
                  >抽取</a-button
                >
              </a-input-group>
            </div>
          </div>
        </div>
      </a-tab-pane>
    </a-tabs>

    <!-- 弹窗放在 a-tabs 外面，避免定位异常 -->
    <a-modal
      v-model:visible="itemModalVisible"
      title="创建知识库条目"
      :confirm-loading="itemSaving"
      :width="560"
      centered
      ok-text="创建条目"
      cancel-text="取消"
      @ok="handleSaveItem"
      @cancel="resetItemForm"
    >
      <a-form :model="itemForm" layout="vertical" class="kb-item-form">
        <a-form-item label="标题" required>
          <a-input v-model:value="itemForm.title" placeholder="请输入条目标题" />
        </a-form-item>
        <a-form-item label="模态类型">
          <a-radio-group v-model:value="itemForm.modality" button-style="solid" class="mode-group">
            <a-radio-button value="text">文本</a-radio-button>
            <a-radio-button value="code">代码</a-radio-button>
            <a-radio-button value="image">图片</a-radio-button>
            <a-radio-button value="audio">音频</a-radio-button>
            <a-radio-button value="video">视频</a-radio-button>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="内容来源">
          <a-radio-group
            v-model:value="itemForm.source_type"
            button-style="solid"
            class="source-group"
          >
            <a-radio-button value="text">直接输入</a-radio-button>
            <a-radio-button value="file">文件上传</a-radio-button>
            <a-radio-button value="url">URL 链接</a-radio-button>
          </a-radio-group>
        </a-form-item>
        <a-form-item v-if="itemForm.source_type === 'text'" label="内容" required>
          <a-textarea v-model:value="itemForm.content" :rows="5" placeholder="请输入知识内容..." />
        </a-form-item>
        <a-form-item v-else-if="itemForm.source_type === 'file'" label="上传文件" required>
          <a-upload
            v-model:file-list="itemFileList"
            :before-upload="handleItemBeforeUpload"
            :remove="handleRemoveItemFile"
          >
            <a-button>选择文件</a-button>
          </a-upload>
        </a-form-item>
        <a-form-item v-else label="URL 链接" required>
          <a-input v-model:value="itemForm.url" placeholder="请输入 URL 链接" />
        </a-form-item>
        <a-form-item label="元数据（JSON，可选）">
          <a-textarea
            v-model:value="itemForm.metadataText"
            :rows="2"
            placeholder='例如：{"tag": "demo"}'
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal
      v-model:visible="entityModalVisible"
      :title="entityModalMode === 'create' ? '新建实体' : '编辑实体'"
      :confirm-loading="entitySaving"
      centered
      @ok="handleSaveEntity"
    >
      <a-form :model="entityForm" layout="vertical" class="entity-modal-form">
        <a-form-item label="名称" required>
          <a-input v-model:value="entityForm.name" placeholder="请输入实体名称" />
        </a-form-item>
        <a-form-item label="类型" required>
          <div class="entity-type-section">
            <div class="type-preset-grid">
              <a-button
                v-for="t in presetEntityTypes"
                :key="t"
                size="middle"
                :type="entityForm.type === t ? 'primary' : 'default'"
                @click="selectPresetType(t)"
              >
                {{ t }}
              </a-button>
            </div>
            <a-input
              v-model:value="entityForm.customType"
              class="type-custom-input"
              placeholder="或输入自定义类型"
            />
          </div>
        </a-form-item>
        <a-form-item>
          <template #label>
            <div class="entity-props-label-row">
              <span>属性（可选）</span>
              <a-button type="link" @click="addEntityProperty">+ 添加属性</a-button>
            </div>
          </template>
          <div class="entity-props-rows">
            <div
              v-for="(prop, index) in entityForm.properties"
              :key="index"
              class="entity-prop-row"
            >
              <a-input v-model:value="prop.key" placeholder="键" class="prop-key-input" />
              <a-input v-model:value="prop.value" placeholder="值" class="prop-value-input" />
              <a-button
                v-if="entityForm.properties.length > 1"
                type="text"
                danger
                class="prop-remove-btn"
                @click="removeEntityProperty(index)"
              >
                删除
              </a-button>
            </div>
          </div>
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal
      v-model:visible="relationModalVisible"
      title="新建关系"
      :confirm-loading="relationSaving"
      centered
      @ok="handleSaveRelation"
    >
      <a-form :model="relationForm" layout="vertical">
        <a-form-item label="源实体" required>
          <a-select
            v-model:value="relationForm.source"
            :options="entityOptions"
            placeholder="选择源实体"
            show-search
            option-filter-prop="label"
          />
        </a-form-item>
        <a-form-item label="目标实体" required>
          <a-select
            v-model:value="relationForm.target"
            :options="entityOptions"
            placeholder="选择目标实体"
            show-search
            option-filter-prop="label"
          />
        </a-form-item>
        <a-form-item label="关系类型" required>
          <a-input
            v-model:value="relationForm.relation_type"
            placeholder="例如：related_to、depends_on 等"
          />
        </a-form-item>
        <a-form-item label="来源片段 ID（可选）">
          <a-input-number
            v-model:value="relationForm.source_chunk"
            :min="1"
            style="width: 100%"
            placeholder="如果关系来自某个片段，可填写对应片段 ID"
          />
        </a-form-item>
        <a-form-item label="属性（JSON，可选）">
          <a-textarea
            v-model:value="relationForm.propertiesText"
            :rows="3"
            placeholder='例如：{"weight": 0.9}'
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';
import { message } from 'ant-design-vue';
import {
  BookOutlined,
  SearchOutlined,
  DeploymentUnitOutlined,
  PlusOutlined,
  LinkOutlined,
  ArrowRightOutlined,
  EditOutlined,
  DeleteOutlined,
  NodeIndexOutlined,
} from '@ant-design/icons-vue';
import { kbApi, type KbItem } from '@/api/kb';

const activeTab = ref('items');

// 条目列表
const itemsLoading = ref(false);
const itemsQuery = ref('');
const items = ref<KbItem[]>([]);
const itemsPage = reactive({ current: 1, pageSize: 6 });
const itemsTotal = ref(0);

const textItemsCount = computed(() => items.value.filter((i) => i.modality === 'text').length);
const codeItemsCount = computed(() => items.value.filter((i) => i.modality === 'code').length);
const currentPageChunkCount = computed(() =>
  items.value.reduce((sum, i) => sum + (typeof i.chunk_count === 'number' ? i.chunk_count : 0), 0)
);

const fetchItems = async () => {
  try {
    itemsLoading.value = true;
    const res = await kbApi.listItems({
      query: itemsQuery.value || undefined,
      page: itemsPage.current,
      page_size: itemsPage.pageSize,
    });
    items.value = res.data?.list || [];
    itemsTotal.value = res.data?.total || 0;
  } catch (e: any) {
    message.error(e?.message || '获取知识条目失败');
  } finally {
    itemsLoading.value = false;
  }
};

const handleItemsSearch = () => {
  itemsPage.current = 1;
  fetchItems();
};

const handleItemsPageChange = (page: number, pageSize: number) => {
  itemsPage.current = page;
  itemsPage.pageSize = pageSize;
  fetchItems();
};

const itemModalVisible = ref(false);
const itemSaving = ref(false);
const itemForm = reactive({
  title: '',
  modality: 'text' as string,
  source_type: 'text' as 'text' | 'file' | 'url',
  content: '',
  url: '',
  metadataText: '',
});
const itemFileList = ref<any[]>([]);

const openItemModal = () => {
  resetItemForm();
  itemModalVisible.value = true;
};

const resetItemForm = () => {
  itemForm.title = '';
  itemForm.modality = 'text';
  itemForm.source_type = 'text';
  itemForm.content = '';
  itemForm.url = '';
  itemForm.metadataText = '';
  itemFileList.value = [];
};

const handleItemBeforeUpload = (file: any) => {
  itemFileList.value = [file];
  return false;
};

const handleRemoveItemFile = () => {
  itemFileList.value = [];
};

const handleSaveItem = async () => {
  const title = itemForm.title?.trim();
  if (!title) {
    message.warning('请输入条目标题');
    return;
  }

  try {
    itemSaving.value = true;
    const modality = itemForm.modality || 'text';
    const sourceType = itemForm.source_type || 'text';

    let metadata: any | undefined;
    if (itemForm.metadataText && itemForm.metadataText.trim()) {
      try {
        metadata = JSON.parse(itemForm.metadataText);
      } catch {
        message.error('元数据必须是合法的 JSON');
        return;
      }
    }

    if (sourceType === 'text') {
      const content = itemForm.content?.trim();
      if (!content) {
        message.warning('请输入知识内容');
        return;
      }
    } else if (sourceType === 'file') {
      if (!itemFileList.value.length) {
        message.warning('请选择文件');
        return;
      }
    } else if (sourceType === 'url') {
      const url = itemForm.url?.trim();
      if (!url) {
        message.warning('请输入 URL 链接');
        return;
      }
    }

    if (sourceType === 'file') {
      const fileRecord: any = itemFileList.value[0];
      const rawFile = fileRecord.originFileObj || fileRecord;
      const formData = new FormData();
      formData.append('title', title);
      formData.append('modality', modality);
      formData.append('source_type', 'file');
      formData.append('file', rawFile);
      if (metadata !== undefined) {
        formData.append('metadata', JSON.stringify(metadata));
      }
      await kbApi.createItemFile(formData);
    } else {
      const payload: any = {
        title,
        modality,
        source_type: sourceType,
        metadata,
      };
      if (sourceType === 'text') {
        payload.content = itemForm.content || undefined;
      } else if (sourceType === 'url') {
        // 按文档仅定义了 content/file 字段，这里将 URL 作为 content 传递
        payload.content = itemForm.url || undefined;
      }
      await kbApi.createItemJson(payload);
    }

    message.success('创建知识条目成功');
    itemModalVisible.value = false;
    resetItemForm();
    fetchItems();
  } catch (e: any) {
    message.error(e?.message || '创建知识条目失败');
  } finally {
    itemSaving.value = false;
  }
};

// 智能问答
interface QaSource {
  item_id?: number;
  item_title?: string;
  chunk_id?: number;
  [key: string]: any;
}

interface QaMessage {
  id: number;
  type: 'question' | 'answer' | 'loading';
  content: string;
  sources?: QaSource[];
}

const qaQuestion = ref('');
const qaK = ref(5);
const qaLoading = ref(false);
const qaMessages = ref<QaMessage[]>([]);
const qaMessagesRef = ref<HTMLDivElement | null>(null);
let qaMessageId = 0;

const addQaMessage = (msg: Omit<QaMessage, 'id'>): QaMessage => {
  const full: QaMessage = { id: ++qaMessageId, ...msg };
  qaMessages.value.push(full);
  return full;
};

const scrollQaToBottom = () => {
  nextTick(() => {
    const el = qaMessagesRef.value;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  });
};

const handleQaPressEnter = (e: KeyboardEvent) => {
  if (!e.shiftKey) {
    e.preventDefault();
    handleQaSubmit();
  }
};

const handleQaSubmit = async () => {
  const question = qaQuestion.value.trim();
  if (!question) {
    message.warning('请输入问题');
    return;
  }

  // 先追加用户问题和加载状态
  addQaMessage({ type: 'question', content: question });
  const loadingMsg = addQaMessage({ type: 'loading', content: '' });
  scrollQaToBottom();

  try {
    qaLoading.value = true;
    const res = await kbApi.qa({ question, k: qaK.value });
    const data: any = res.data || {};

    // 移除 loading 消息
    qaMessages.value = qaMessages.value.filter((m) => m.id !== loadingMsg.id);

    addQaMessage({
      type: 'answer',
      content: data.answer || '（未返回回答内容）',
      // 后端可选返回 sources / references，均做兼容
      sources: data.sources || data.references || [],
    });
  } catch (e: any) {
    qaMessages.value = qaMessages.value.filter((m) => m.id !== loadingMsg.id);
    message.error(e?.message || '获取回答失败');
  } finally {
    qaLoading.value = false;
    qaQuestion.value = '';
    scrollQaToBottom();
  }
};

// 图谱
const graphLoading = ref(false);
const entities = ref<any[]>([]);
const relations = ref<any[]>([]);
const entitiesTotal = ref(0);
const relationsTotal = ref(0);

const selectedEntityId = ref<number | null>(null);

const entityModalVisible = ref(false);
const entityModalMode = ref<'create' | 'edit'>('create');
const entitySaving = ref(false);
const entityForm = reactive({
  id: 0 as number | null,
  name: '',
  type: '',
  customType: '',
  properties: [] as { key: string; value: string }[],
});

const presetEntityTypes = [
  'Framework',
  'Library',
  'Language',
  'Feature',
  'Component',
  'Concept',
  'Tool',
  'Platform',
  'Service',
];

const relationModalVisible = ref(false);
const relationSaving = ref(false);
const relationForm = reactive({
  source: undefined as number | undefined,
  target: undefined as number | undefined,
  relation_type: '',
  propertiesText: '',
  source_chunk: undefined as number | undefined,
});

const resetRelationForm = () => {
  relationForm.source = undefined;
  relationForm.target = undefined;
  relationForm.relation_type = '';
  relationForm.propertiesText = '';
  relationForm.source_chunk = undefined;
};

const handleSaveRelation = async () => {
  if (!relationForm.source || !relationForm.target) {
    message.warning('请选择源实体和目标实体');
    return;
  }
  if (!relationForm.relation_type.trim()) {
    message.warning('请输入关系类型');
    return;
  }

  let properties: any | undefined;
  if (relationForm.propertiesText && relationForm.propertiesText.trim()) {
    try {
      properties = JSON.parse(relationForm.propertiesText);
    } catch {
      message.error('关系属性必须是合法的 JSON');
      return;
    }
  }

  const payload: any = {
    source: relationForm.source,
    target: relationForm.target,
    relation_type: relationForm.relation_type.trim(),
  };
  if (properties !== undefined) payload.properties = properties;
  if (relationForm.source_chunk) payload.source_chunk = relationForm.source_chunk;

  try {
    relationSaving.value = true;
    await kbApi.createRelation(payload);
    message.success('创建关系成功');
    relationModalVisible.value = false;
    resetRelationForm();
    await fetchGraph();
  } catch (e: any) {
    message.error(e?.message || '创建关系失败');
  } finally {
    relationSaving.value = false;
  }
};

const extractText = ref('');
const extractItemId = ref<number | null>(null);
const extractLoading = ref(false);

const graphWidth = 600;
const graphHeight = 360;

interface GraphNode {
  id: number;
  name: string;
  x: number;
  y: number;
  isCenter: boolean;
  raw: any;
}

interface GraphLink {
  id: number | string;
  relation_type?: string;
  sourceNode: GraphNode;
  targetNode: GraphNode;
}

const entityTableColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '类型', dataIndex: 'type', key: 'type' },
  { title: '关系数', key: 'relationCount' },
  { title: '操作', key: 'actions', width: 100 },
];

const relationColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id' },
  { title: '源实体', dataIndex: 'source', key: 'source' },
  { title: '目标实体', dataIndex: 'target', key: 'target' },
  { title: '关系类型', dataIndex: 'relation_type', key: 'relation_type' },
  { title: '操作', key: 'actions' },
];

const entityOptions = computed(() =>
  (entities.value || []).map((e: any) => ({
    label: e.name ?? String(e.id),
    value: e.id,
  }))
);
// --- 图谱统计 & 选择 ---
const getEntityRelationCount = (id: number) =>
  (relations.value || []).filter((r: any) => r.source === id || r.target === id).length;

const entityTypesCount = computed(() => {
  const types = new Set((entities.value || []).map((e: any) => e.type).filter(Boolean));
  return types.size;
});

const relationTypesCount = computed(() => {
  const types = new Set((relations.value || []).map((r: any) => r.relation_type).filter(Boolean));
  return types.size;
});

const selectedEntity = computed(() => {
  if (!entities.value.length) return null;
  if (selectedEntityId.value == null) return entities.value[0];
  return entities.value.find((e: any) => e.id === selectedEntityId.value) || entities.value[0];
});

const selectedEntityRelations = computed(() => {
  if (!selectedEntity.value) return [];
  const eid = selectedEntity.value.id;
  return (relations.value || []).filter((r: any) => r.source === eid || r.target === eid);
});

const selectEntity = (id: number) => {
  selectedEntityId.value = id;
};

const getEntityName = (id: number) => {
  const list = entities.value || [];
  const found = list.find((e: any) => e.id === id);
  return found?.name ?? id;
};

const resetEntityForm = () => {
  entityForm.id = null;
  entityForm.name = '';
  entityForm.type = '';
  entityForm.customType = '';
  entityForm.properties = [];
};

const openEntityModal = (mode: 'create' | 'edit', record?: any) => {
  entityModalMode.value = mode;
  if (mode === 'create') {
    resetEntityForm();
  } else if (record) {
    entityForm.id = record.id ?? null;
    entityForm.name = record.name || '';
    const recordType = record.type || '';
    if (presetEntityTypes.includes(recordType)) {
      entityForm.type = recordType;
      entityForm.customType = '';
    } else {
      entityForm.type = '';
      entityForm.customType = recordType;
    }

    let propsObj: any = {};
    const rawProps = record.properties;
    if (rawProps) {
      if (typeof rawProps === 'string') {
        try {
          propsObj = JSON.parse(rawProps);
        } catch {
          propsObj = {};
        }
      } else if (typeof rawProps === 'object') {
        propsObj = rawProps;
      }
    }

    const entries = Object.entries(propsObj);
    entityForm.properties = entries.length
      ? entries.map(([key, value]) => ({ key, value: String(value) }))
      : [];
  }
  entityModalVisible.value = true;
};

const selectPresetType = (t: string) => {
  entityForm.type = t;
  entityForm.customType = '';
};

const addEntityProperty = () => {
  entityForm.properties.push({ key: '', value: '' });
};

const removeEntityProperty = (index: number) => {
  if (entityForm.properties.length <= 1) return;
  entityForm.properties.splice(index, 1);
};

const handleSaveEntity = async () => {
  const name = entityForm.name.trim();
  if (!name) {
    message.warning('请输入实体名称');
    return;
  }

  const finalType = (entityForm.customType || entityForm.type).trim();
  if (!finalType) {
    message.warning('请选择或输入实体类型');
    return;
  }

  const propsObj: any = {};
  entityForm.properties.forEach(({ key, value }) => {
    const k = (key || '').trim();
    if (!k) return;
    propsObj[k] = value;
  });

  const payload: any = {
    name,
    type: finalType,
  };
  if (Object.keys(propsObj).length > 0) {
    payload.properties = propsObj;
  }

  try {
    entitySaving.value = true;
    if (entityModalMode.value === 'create' || !entityForm.id) {
      await kbApi.createEntity(payload);
      message.success('创建实体成功');
    } else {
      await kbApi.updateEntity(entityForm.id, payload);
      message.success('更新实体成功');
    }
    entityModalVisible.value = false;
    resetEntityForm();
    await fetchGraph();
  } catch (e: any) {
    message.error(
      e?.message || (entityModalMode.value === 'create' ? '创建实体失败' : '更新实体失败')
    );
  } finally {
    entitySaving.value = false;
  }
};

const handleDeleteEntity = async (id: number) => {
  try {
    await kbApi.deleteEntity(id);
    message.success('删除实体成功');
    if (selectedEntityId.value === id) {
      selectedEntityId.value = null;
    }
    await fetchGraph();
  } catch (e: any) {
    message.error(e?.message || '删除实体失败');
  }
};

// --- Canvas 图谱可视化（静态布局版本） ---
const canvasWrapperRef = ref<HTMLDivElement | null>(null);
const graphCanvasRef = ref<HTMLCanvasElement | null>(null);

interface CanvasNode {
  id: number;
  name: string;
  type: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  fx?: number; // 拖拽时固定X坐标
  fy?: number; // 拖拽时固定Y坐标
}

interface CanvasLink {
  sourceId: number;
  targetId: number;
  relation_type?: string;
}

let canvasNodes: CanvasNode[] = [];
let canvasLinks: CanvasLink[] = [];
let ctx: CanvasRenderingContext2D | null = null;
let canvasWidth = 0;
let canvasHeight = 0;
let animationFrameId = 0;
let isDragging = false;
let dragNode: CanvasNode | null = null;
let lastMouseX = 0;
let lastMouseY = 0;

// 力导向布局参数（参考 GRAPH_VISUALIZATION_SPEC.md）
const REPULSION = 3000; // 排斥力强度
const ATTRACTION = 0.01; // 吸引力强度
const CENTER_ATTRACTION = 0.001; // 中心吸引力强度
const DAMPING = 0.9; // 阻尼系数
const PADDING = 50; // 边界内边距
const REPULSION_RANGE = 300; // 排斥力作用范围
const BASE_RADIUS = 30; // 节点基础半径
const SELECTED_RADIUS = 35; // 选中节点半径
const ARROW_SIZE = 8; // 箭头大小
const CURVE_OFFSET = 20; // 曲线弯曲偏移量

const setupCanvas = () => {
  const wrapper = canvasWrapperRef.value;
  const canvas = graphCanvasRef.value;
  if (!wrapper || !canvas) return;

  // 避免重复动画循环
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
    animationFrameId = 0;
  }

  const rect = wrapper.getBoundingClientRect();
  canvasWidth = rect.width;
  canvasHeight = rect.height || 400;

  const dpr = window.devicePixelRatio || 1;
  canvas.width = canvasWidth * dpr;
  canvas.height = canvasHeight * dpr;
  ctx = canvas.getContext('2d');
  if (!ctx) return;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

  // 基于当前实体 / 关系计算一次布局并启动动画
  layoutCanvasGraph();
  drawCanvasGraph();
  animate();
};

const layoutCanvasGraph = () => {
  const list = entities.value || [];
  const oldMap = new Map<number, CanvasNode>(canvasNodes.map((n) => [n.id, n]));
  canvasNodes = [];
  canvasLinks = [];

  if (!list.length || !canvasWidth || !canvasHeight) return;

  const centerX = canvasWidth / 2;
  const centerY = canvasHeight / 2;
  const radiusBase = Math.min(canvasWidth, canvasHeight) * 0.25;

  // 圆形初始布局（参考 GRAPH_VISUALIZATION_SPEC.md 第五章）
  list.forEach((e: any, idx: number) => {
    const prev = oldMap.get(e.id);
    if (prev) {
      // 复用原来的坐标和速度，避免每次重算导致跳变
      canvasNodes.push({
        ...prev,
        name: e.name || String(e.id),
        type: e.type || prev.type,
      });
    } else {
      const angle = (idx / list.length) * Math.PI * 2;
      // 初始位置加一点随机扰动，避免节点完全重叠
      const x = centerX + radiusBase * Math.cos(angle) + (Math.random() - 0.5) * 50;
      const y = centerY + radiusBase * Math.sin(angle) + (Math.random() - 0.5) * 50;
      canvasNodes.push({
        id: e.id,
        name: e.name || String(e.id),
        type: e.type || 'Node',
        x,
        y,
        vx: 0,
        vy: 0,
        fx: undefined,
        fy: undefined,
      });
    }
  });

  // 构造连线
  canvasLinks = (relations.value || []).map((r: any) => ({
    sourceId: r.source,
    targetId: r.target,
    relation_type: r.relation_type,
  }));
};

// 类型颜色映射（参考 GRAPH_VISUALIZATION_SPEC.md）
const TYPE_COLORS: Record<string, string> = {
  Framework: '#3b82f6', // blue-500
  Library: '#8b5cf6', // violet-500
  Language: '#ef4444', // red-500
  Feature: '#10b981', // green-500
  Component: '#f59e0b', // amber-500
  Concept: '#06b6d4', // cyan-500
  Tool: '#84cc16', // lime-500
  Platform: '#f472b6', // pink-400
  Service: '#a855f7', // purple-500
};
const DEFAULT_COLOR = '#6366f1'; // indigo-500

const getTypeColor = (type: string): string => {
  return TYPE_COLORS[type] || DEFAULT_COLOR;
};

const drawCanvasGraph = () => {
  if (!ctx) return;
  ctx.clearRect(0, 0, canvasWidth, canvasHeight);

  // 预先建索引
  const nodeMap = new Map(canvasNodes.map((n) => [n.id, n]));

  // ========== 1. 绘制关系线（二次贝塞尔曲线 + 箭头 + 标签）==========
  ctx.lineWidth = 2;
  ctx.strokeStyle = '#cbd5e1'; // slate-300

  canvasLinks.forEach((link) => {
    const s = nodeMap.get(link.sourceId);
    const t = nodeMap.get(link.targetId);
    if (!s || !t) return;

    // 计算控制点（曲线弯曲）
    const midX = (s.x + t.x) / 2;
    const midY = (s.y + t.y) / 2;
    const dx = t.x - s.x;
    const dy = t.y - s.y;
    const controlX = midX - (dy * CURVE_OFFSET) / 100;
    const controlY = midY + (dx * CURVE_OFFSET) / 100;

    // 绘制曲线
    ctx!.beginPath();
    ctx!.moveTo(s.x, s.y);
    ctx!.quadraticCurveTo(controlX, controlY, t.x, t.y);
    ctx!.stroke();

    // 绘制箭头
    const angle = Math.atan2(t.y - controlY, t.x - controlX);
    ctx!.beginPath();
    ctx!.moveTo(t.x, t.y);
    ctx!.lineTo(
      t.x - ARROW_SIZE * Math.cos(angle - Math.PI / 6),
      t.y - ARROW_SIZE * Math.sin(angle - Math.PI / 6)
    );
    ctx!.lineTo(
      t.x - ARROW_SIZE * Math.cos(angle + Math.PI / 6),
      t.y - ARROW_SIZE * Math.sin(angle + Math.PI / 6)
    );
    ctx!.closePath();
    ctx!.fillStyle = '#cbd5e1';
    ctx!.fill();

    // 关系标签
    if (link.relation_type) {
      ctx!.fillStyle = '#64748b'; // slate-500
      ctx!.font = '11px sans-serif';
      ctx!.textAlign = 'center';
      ctx!.textBaseline = 'middle';
      ctx!.fillText(link.relation_type, controlX, controlY);
    }
  });

  // ========== 2. 绘制节点（渐变圆形 + 边框 + 阴影 + 文本 + 类型标签）==========
  canvasNodes.forEach((node) => {
    const isSelected = node.id === selectedEntityId.value;
    const isDrag = isDragging && dragNode?.id === node.id;
    const nodeRadius = isSelected || isDrag ? SELECTED_RADIUS : BASE_RADIUS;
    const baseColor = getTypeColor(node.type);

    // 选中/拖拽时的阴影效果
    if (isSelected || isDrag) {
      ctx!.shadowColor = 'rgba(59, 130, 246, 0.3)';
      ctx!.shadowBlur = 15;
    }

    // 渐变填充
    const gradient = ctx!.createRadialGradient(
      node.x - nodeRadius / 3, // 光源偏移
      node.y - nodeRadius / 3,
      0,
      node.x,
      node.y,
      nodeRadius
    );
    gradient.addColorStop(0, baseColor + 'dd'); // 中心亮 (透明度 87%)
    gradient.addColorStop(1, baseColor); // 边缘暗

    // 绘制圆形
    ctx!.beginPath();
    ctx!.arc(node.x, node.y, nodeRadius, 0, Math.PI * 2);
    ctx!.fillStyle = gradient;
    ctx!.fill();

    // 边框
    ctx!.strokeStyle = isSelected || isDrag ? '#1e40af' : '#ffffff'; // blue-800 / white
    ctx!.lineWidth = isSelected || isDrag ? 3 : 2;
    ctx!.stroke();

    // 重置阴影
    ctx!.shadowColor = 'transparent';
    ctx!.shadowBlur = 0;

    // 节点名称（截断处理）
    ctx!.fillStyle = '#ffffff';
    ctx!.font = 'bold 12px sans-serif';
    ctx!.textAlign = 'center';
    ctx!.textBaseline = 'middle';
    const text = node.name.length > 8 ? node.name.substring(0, 7) + '...' : node.name;
    ctx!.fillText(text, node.x, node.y);

    // 类型标签（节点下方）
    ctx!.fillStyle = '#ffffff';
    ctx!.font = '9px sans-serif';
    ctx!.fillText(node.type, node.x, node.y + nodeRadius + 12);
  });
};

// 力导向布局更新（参考 GRAPH_VISUALIZATION_SPEC.md 第三章）
const updateForces = () => {
  const nodes = canvasNodes;
  const links = canvasLinks;
  const n = nodes.length;
  if (!n) return;

  const cx = canvasWidth / 2;
  const cy = canvasHeight / 2;
  const nodeMap = new Map(nodes.map((node) => [node.id, node]));

  nodes.forEach((node) => {
    // 跳过被拖拽固定的节点
    if (node.fx !== undefined && node.fy !== undefined) {
      node.x = node.fx;
      node.y = node.fy;
      return;
    }

    // ========== 1. 排斥力（节点间）==========
    // 只计算距离 < REPULSION_RANGE 的节点对
    nodes.forEach((other) => {
      if (node.id === other.id) return;
      const dx = node.x - other.x;
      const dy = node.y - other.y;
      const distSq = dx * dx + dy * dy;
      const dist = Math.sqrt(distSq) || 1;

      if (dist < REPULSION_RANGE) {
        const force = REPULSION / distSq;
        node.vx += (dx / dist) * force;
        node.vy += (dy / dist) * force;
      }
    });

    // ========== 2. 吸引力（有连接的节点对）==========
    links.forEach((link) => {
      let other: CanvasNode | undefined;
      if (link.sourceId === node.id) other = nodeMap.get(link.targetId);
      else if (link.targetId === node.id) other = nodeMap.get(link.sourceId);

      if (other) {
        const dx = other.x - node.x;
        const dy = other.y - node.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = dist * ATTRACTION;
        node.vx += (dx / dist) * force;
        node.vy += (dy / dist) * force;
      }
    });

    // ========== 3. 中心吸引力 ==========
    const dxCenter = cx - node.x;
    const dyCenter = cy - node.y;
    node.vx += dxCenter * CENTER_ATTRACTION;
    node.vy += dyCenter * CENTER_ATTRACTION;

    // ========== 4. 应用阻尼和更新位置 ==========
    node.vx *= DAMPING;
    node.vy *= DAMPING;
    node.x += node.vx;
    node.y += node.vy;

    // ========== 5. 边界约束 ==========
    if (node.x < PADDING) {
      node.x = PADDING;
      node.vx = 0;
    }
    if (node.x > canvasWidth - PADDING) {
      node.x = canvasWidth - PADDING;
      node.vx = 0;
    }
    if (node.y < PADDING) {
      node.y = PADDING;
      node.vy = 0;
    }
    if (node.y > canvasHeight - PADDING) {
      node.y = canvasHeight - PADDING;
      node.vy = 0;
    }
  });
};

const animate = () => {
  animationFrameId = window.requestAnimationFrame(animate);
  updateForces();
  drawCanvasGraph();
};

// 命中测试（点击检测半径 = SELECTED_RADIUS）
const CLICK_RADIUS = 35;
const pickNodeAt = (x: number, y: number): CanvasNode | null => {
  for (let i = canvasNodes.length - 1; i >= 0; i -= 1) {
    const n = canvasNodes[i];
    const dx = x - n.x;
    const dy = y - n.y;
    if (dx * dx + dy * dy <= CLICK_RADIUS * CLICK_RADIUS) return n;
  }
  return null;
};

// 鼠标按下（参考 GRAPH_VISUALIZATION_SPEC.md 第五章）
const handleCanvasMouseDown = (e: MouseEvent) => {
  if (!graphCanvasRef.value) return;
  const rect = graphCanvasRef.value.getBoundingClientRect();
  const mouseX = e.clientX - rect.left;
  const mouseY = e.clientY - rect.top;
  const node = pickNodeAt(mouseX, mouseY);

  if (node) {
    // 选中并开始拖拽
    selectEntity(node.id);
    isDragging = true;
    dragNode = node;
    // 固定节点位置
    node.fx = mouseX;
    node.fy = mouseY;
    node.vx = 0;
    node.vy = 0;
    graphCanvasRef.value.style.cursor = 'grabbing';
  } else {
    // 点击空白取消选中
    selectedEntityId.value = null;
  }
};

// 鼠标移动
const handleCanvasMouseMove = (e: MouseEvent) => {
  if (!graphCanvasRef.value) return;
  const rect = graphCanvasRef.value.getBoundingClientRect();
  const mouseX = e.clientX - rect.left;
  const mouseY = e.clientY - rect.top;

  if (isDragging && dragNode) {
    // 更新固定位置
    dragNode.fx = mouseX;
    dragNode.fy = mouseY;
    dragNode.x = mouseX;
    dragNode.y = mouseY;
    dragNode.vx = 0;
    dragNode.vy = 0;
    graphCanvasRef.value.style.cursor = 'grabbing';
    return;
  }

  const node = pickNodeAt(mouseX, mouseY);
  graphCanvasRef.value.style.cursor = node ? 'pointer' : 'grab';
};

// 鼠标释放
const handleCanvasMouseUp = () => {
  if (isDragging && dragNode) {
    // 解除固定，恢复物理模拟
    dragNode.fx = undefined;
    dragNode.fy = undefined;
  }
  isDragging = false;
  dragNode = null;
  if (graphCanvasRef.value) graphCanvasRef.value.style.cursor = 'grab';
};

// 鼠标离开
const handleCanvasMouseLeave = () => {
  if (isDragging && dragNode) {
    dragNode.fx = undefined;
    dragNode.fy = undefined;
  }
  isDragging = false;
  dragNode = null;
  if (graphCanvasRef.value) graphCanvasRef.value.style.cursor = 'grab';
};

onUnmounted(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
    animationFrameId = 0;
  }
});

// 获取图谱数据
const fetchGraph = async () => {
  try {
    graphLoading.value = true;
    const entityRes = await kbApi.listEntities({ page: 1, page_size: 100 });
    const relationRes = await kbApi.listRelations({ page: 1, page_size: 100 });

    const eData: any = entityRes.data || {};
    const rData: any = relationRes.data || {};

    entities.value = eData.list || eData || [];
    relations.value = rData.list || rData || [];

    entitiesTotal.value = eData.total ?? entities.value.length;
    relationsTotal.value = rData.total ?? relations.value.length;

    if (entities.value.length && selectedEntityId.value == null) {
      selectedEntityId.value = entities.value[0].id;
    }

    // 等待 DOM 渲染完成后初始化画布
    await nextTick();
    setupCanvas();
  } catch (e: any) {
    message.error(e?.message || '获取知识图谱数据失败');
  } finally {
    graphLoading.value = false;
  }
};

const handleExtractFromText = async () => {
  if (!extractText.value.trim()) {
    message.warning('请输入要抽取的文本');
    return;
  }
  try {
    extractLoading.value = true;
    const res = await kbApi.extractGraph({ text: extractText.value });
    const d: any = res.data || {};
    message.success(`抽取完成：实体 ${d.entities ?? 0} 个，关系 ${d.relations ?? 0} 条`);
    fetchGraph();
  } catch (e: any) {
    message.error(e?.message || '从文本抽取图谱失败');
  } finally {
    extractLoading.value = false;
  }
};

const handleExtractFromItem = async () => {
  if (!extractItemId.value) {
    message.warning('请输入知识条目 ID');
    return;
  }
  try {
    extractLoading.value = true;
    const res = await kbApi.extractGraph({ item_id: extractItemId.value });
    const d: any = res.data || {};
    message.success(`抽取完成：实体 ${d.entities ?? 0} 个，关系 ${d.relations ?? 0} 条`);
    fetchGraph();
  } catch (e: any) {
    message.error(e?.message || '从条目抽取图谱失败');
  } finally {
    extractLoading.value = false;
  }
};

const formatDate = (val?: string) => {
  if (!val) return '-';
  const d = new Date(val);
  if (Number.isNaN(d.getTime())) return val;
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const formatProperties = (props: any) => {
  if (!props) return '-';
  if (typeof props === 'string') return props;
  try {
    return JSON.stringify(props);
  } catch {
    return String(props);
  }
};

watch(activeTab, (key) => {
  if (key === 'items' && !items.length) fetchItems();
  if (key === 'graph' && !entities.value.length && !relations.value.length) fetchGraph();
});

onMounted(() => {
  fetchItems();
});
</script>

<style scoped lang="scss">
@import '@/styles/variables';

.kb-center {
  padding: 24px;
  background: var(--theme-page-bg, #f5f5f5);
  min-height: 100vh;

  .page-header {
    margin-bottom: 16px;
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

  .kb-tabs {
    max-width: 1200px;
    margin: 0 auto;
  }

  .tab-section {
    background: var(--theme-card-bg, #fff);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    border: 1px solid var(--theme-card-border, #e5e7eb);
  }

  .items-search-row {
    margin-bottom: 16px;
  }

  .items-toolbar {
    margin-bottom: 16px;
    display: flex;
    justify-content: flex-end;
  }

  .stats-row {
    margin-bottom: 16px;

    .stat-card {
      background: var(--theme-content-bg, #f8fafc);
      border-radius: 10px;
      padding: 12px 16px;
      border: 1px solid var(--theme-card-border, #e5e7eb);

      .stat-label {
        font-size: 13px;
        color: var(--theme-text-secondary, #64748b);
        margin-bottom: 4px;
      }

      .stat-value {
        font-size: 20px;
        font-weight: 700;
        color: var(--theme-text-primary, #1e293b);
      }

      &.small {
        padding: 10px 14px;

        .stat-value {
          font-size: 18px;
        }
      }
    }
  }

  .items-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 16px;

    .item-card {
      background: #fff;
      border-radius: 12px;
      border: 1px solid var(--theme-card-border, #e5e7eb);
      padding: 16px 18px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      transition: all 0.3s ease;

      &:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        border-color: var(--theme-primary, #3b82f6);
      }

      .item-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 8px;

        .item-title {
          font-size: 16px;
          font-weight: 600;
          color: var(--theme-text-primary, #1e293b);
        }

        .item-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
        }
      }

      .item-meta {
        display: flex;
        flex-direction: column;
        gap: 4px;

        .meta-row {
          display: flex;
          justify-content: space-between;
          font-size: 13px;

          .meta-label {
            color: var(--theme-text-secondary, #64748b);
          }

          .meta-value {
            color: var(--theme-text-primary, #1e293b);
            font-weight: 500;
          }
        }
      }

      .graph-extract-card {
        background: #fff;
        border-radius: 12px;
        border: 1px solid var(--theme-card-border, #e5e7eb);
        padding: 12px 16px;

        .graph-table-title {
          margin: 0 0 8px;
          font-size: 14px;
          font-weight: 600;
        }

        .graph-extract-controls {
          display: flex;
          flex-direction: column;
          gap: 8px;
          font-size: 12px;
          color: var(--theme-text-secondary, #64748b);
        }

        .graph-extract-tip {
          font-size: 12px;
          color: var(--theme-text-secondary, #94a3b8);
        }
      }
    }
  }

  .pagination-wrapper {
    margin-top: 16px;
    display: flex;
    justify-content: center;
  }

  .tab-empty {
    padding: 48px 0;
  }

  // 智能问答面板样式
  .qa-panel {
    display: flex;
    flex-direction: column;
    gap: 24px;

    .qa-header-card {
      background: #fff;
      border-radius: 12px;
      border: 1px solid var(--theme-card-border, #e5e7eb);
      padding: 20px 24px;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);

      .qa-header-main {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 24px;

        .qa-header-text {
          flex: 1;

          .qa-header-title-row {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;

            .qa-header-icon {
              font-size: 20px;
              color: #9333ea;
            }

            .qa-header-title {
              margin: 0;
              font-size: 18px;
              font-weight: 600;
              color: #0f172a;
            }
          }

          .qa-header-desc {
            margin: 0;
            font-size: 13px;
            color: #475569;
          }
        }

        .qa-header-controls {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          color: #64748b;

          .qa-header-select {
            min-width: 96px;
          }
        }
      }
    }

    .qa-chat-card {
      background: #fff;
      border-radius: 12px;
      border: 1px solid var(--theme-card-border, #e5e7eb);
      display: flex;
      flex-direction: column;

      .qa-messages {
        height: 500px;
        overflow-y: auto;
        padding: 20px 24px;
        background: #f8fafc;
        border-bottom: 1px solid #e2e8f0;
        display: flex;
        flex-direction: column;
        gap: 16px;
      }

      .qa-message-row {
        display: flex;

        &.qa-message-row-question {
          justify-content: flex-end;
        }

        &.qa-message-row-answer {
          justify-content: flex-start;
        }
      }

      .qa-bubble {
        max-width: 80%;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 14px;
        line-height: 1.6;

        .qa-bubble-header {
          display: flex;
          align-items: center;
          gap: 6px;
          margin-bottom: 6px;

          .qa-bubble-label {
            font-size: 12px;
            opacity: 0.9;
          }
        }

        .qa-bubble-content {
          white-space: pre-wrap;
        }
      }

      .qa-bubble-question {
        background: #2563eb;
        color: #ffffff;

        .qa-bubble-header-question {
          .qa-bubble-label {
            color: #e0edff;
          }
        }
      }

      .qa-bubble-answer {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        color: #0f172a;
        display: flex;
        flex-direction: column;
        gap: 8px;

        .qa-bubble-header-answer .qa-bubble-label {
          color: #4b5563;
        }
      }

      .qa-bubble-loading {
        .qa-loading {
          display: flex;
          align-items: center;
          gap: 8px;

          .qa-loading-spinner {
            width: 16px;
            height: 16px;
            border-radius: 999px;
            border: 2px solid #9333ea;
            border-top-color: transparent;
            animation: qa-spin 1s linear infinite;
          }

          .qa-loading-text {
            font-size: 13px;
            color: #475569;
          }
        }
      }

      .qa-empty-state {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #94a3b8;
        font-size: 14px;
        text-align: center;
        padding: 16px 24px;
      }

      .qa-sources {
        margin-top: 4px;
        display: flex;
        flex-direction: column;
        gap: 8px;

        .qa-sources-header {
          font-size: 12px;
          color: #64748b;
        }

        .qa-source-list {
          display: flex;
          flex-direction: column;
          gap: 8px;

          .qa-source-card {
            background: #ffffff;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            padding: 8px 12px;
            font-size: 13px;

            .qa-source-title {
              color: #0f172a;
            }

            .qa-source-meta {
              margin-top: 4px;
              font-size: 12px;
              color: #64748b;
            }
          }
        }
      }

      .qa-input-area {
        padding: 12px 16px 16px 16px;
        border-top: 1px solid #e2e8f0;
        display: flex;
        gap: 12px;
        align-items: flex-end;

        .qa-input {
          flex: 1;
        }
      }
    }
  }

  @keyframes qa-spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }

  // 实体创建弹窗样式
  .entity-modal-form {
    .ant-form-item {
      margin-bottom: 18px;
    }
  }

  .entity-type-section {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .type-preset-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;

      :deep(.ant-btn) {
        width: 100%;
        justify-content: center;
        border-radius: 999px;
        height: 40px;
        padding: 0 12px;
        border-color: #e2e8f0;
        background: #ffffff;
        color: #475569;
        box-shadow: none;
      }

      :deep(.ant-btn:not(.ant-btn-primary):hover) {
        border-color: #93c5fd;
        color: #1d4ed8;
        background: #eff6ff;
      }

      :deep(.ant-btn-primary) {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border-color: transparent;
        color: #ffffff;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.35);
      }
    }

    .type-custom-input {
      margin-top: 4px;
    }
  }

  .entity-props-label-row {
    display: flex;
    justify-content: space-between;
    align-items: center;

    :deep(.ant-btn-link) {
      padding: 0;
      font-size: 12px;
      color: #16a34a;
    }
  }

  .entity-props-rows {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .entity-prop-row {
      display: flex;
      align-items: center;
      gap: 8px;

      .prop-key-input,
      .prop-value-input {
        flex: 1;
      }

      .prop-remove-btn {
        padding: 0 6px;
      }
    }
  }

  .graph-container {
    display: flex;
    flex-direction: column;
    gap: 20px;

    // Header
    .graph-header-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #fff;
      padding: 16px 24px;
      border-radius: 12px;
      border: 1px solid var(--theme-card-border, #e5e7eb);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);

      .header-left {
        .section-title {
          margin: 0 0 4px;
          font-size: 18px;
          font-weight: 600;
          color: #1e293b;
          display: flex;
          align-items: center;
          gap: 8px;

          :deep(.anticon) {
            color: #10b981; // 绿色图标
          }
        }
        .section-desc {
          color: #64748b;
          font-size: 13px;
        }
      }
    }

    // Stats Grid
    .stats-grid-row {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;

      .stat-info-card {
        background: #fff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid var(--theme-card-border, #e5e7eb);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        transition: transform 0.2s;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 12px rgba(0, 0, 0, 0.05);
        }

        .stat-title {
          color: #64748b;
          font-size: 13px;
          font-weight: 500;
          margin-bottom: 8px;
        }
        .stat-num {
          color: #1e293b;
          font-size: 28px;
          font-weight: 700;
          line-height: 1;
        }
      }
    }

    // Main Content Grid
    .graph-main-content {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 20px;
      min-height: 500px;

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;

        .card-title {
          font-size: 16px;
          font-weight: 600;
          color: #334155;
        }
      }

      // Left Canvas Card
      .graph-canvas-card {
        background: #fff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid var(--theme-card-border, #e5e7eb);
        display: flex;
        flex-direction: column;

        .canvas-wrapper {
          flex: 1;
          background: #f8fafc;
          border-radius: 8px;
          border: 1px solid #e2e8f0;
          position: relative;
          overflow: hidden;
          min-height: 400px;

          canvas {
            display: block;
            width: 100%;
            height: 100%;
            cursor: grab;

            &:active {
              cursor: grabbing;
            }
          }

          .canvas-overlay-tip {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            pointer-events: none;
          }
        }

        .canvas-footer {
          margin-top: 12px;
          text-align: center;
          .footer-tip {
            font-size: 12px;
            color: #94a3b8;
          }
        }
      }

      // Right Detail Panel
      .entity-detail-panel {
        background: #fff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid var(--theme-card-border, #e5e7eb);
        display: flex;
        flex-direction: column;

        .detail-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 24px;

          .detail-group {
            .label {
              font-size: 12px;
              color: #94a3b8;
              margin-bottom: 4px;
            }
            .value-lg {
              font-size: 20px;
              font-weight: 600;
              color: #1e293b;
            }
            .value {
              font-size: 14px;
              color: #334155;
            }

            .props-list {
              display: flex;
              flex-direction: column;
              gap: 4px;
              .prop-item {
                font-size: 13px;
                display: flex;
                justify-content: space-between;
                border-bottom: 1px dashed #f1f5f9;
                padding-bottom: 2px;
                .prop-key {
                  color: #64748b;
                }
                .prop-val {
                  color: #334155;
                  font-family: monospace;
                }
              }
            }

            .relations-list {
              display: flex;
              flex-direction: column;
              gap: 8px;
              max-height: 200px;
              overflow-y: auto;

              .no-rel {
                font-size: 13px;
                color: #cbd5e1;
                font-style: italic;
              }

              .rel-item {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 13px;
                background: #f8fafc;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #f1f5f9;

                .rel-type {
                  color: #64748b;
                  font-weight: 500;
                }
                .arrow {
                  color: #cbd5e1;
                  font-size: 10px;
                }
                .rel-target {
                  color: #3b82f6;
                  font-weight: 500;
                }
              }
            }
          }

          .detail-actions {
            margin-top: auto;
            display: flex;
            gap: 10px;
            padding-top: 20px;
            border-top: 1px solid #f1f5f9;
          }
        }

        .detail-empty {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #cbd5e1;

          .empty-state {
            text-align: center;
            .empty-icon {
              font-size: 48px;
              margin-bottom: 12px;
              opacity: 0.5;
            }
            p {
              margin: 0;
              font-size: 13px;
            }
          }
        }
      }
    }

    // Entity List Card
    .entity-list-card {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      border: 1px solid var(--theme-card-border, #e5e7eb);

      .card-header {
        margin-bottom: 16px;
        .card-title {
          font-size: 16px;
          font-weight: 600;
          color: #334155;
        }
      }
    }

    // Extract Card
    .extract-card {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      border: 1px solid var(--theme-card-border, #e5e7eb);

      .card-header {
        margin-bottom: 12px;
        .card-title {
          font-size: 16px;
          font-weight: 600;
          color: #334155;
        }
      }
    }
  }
}

@media (max-width: 1200px) {
  .kb-center .graph-container {
    .stats-grid-row {
      grid-template-columns: repeat(2, 1fr);
    }
  }
}
</style>

<style lang="scss">
/* 全局样式：弹窗内的表单按钮组 */
.kb-item-form {
  .mode-group,
  .source-group {
    display: flex;
    gap: 10px;
    width: 100%;

    .ant-radio-button-wrapper {
      flex: 1;
      text-align: center;
      border-radius: 10px !important;
      border: 1px solid #e2e8f0;
      margin: 0;
      padding: 8px 0;
      height: 42px;
      line-height: 26px;
      box-shadow: none;
      background: #f8fafc;
      color: #64748b;
      font-weight: 500;
      transition: all 0.2s ease;

      &::before {
        display: none;
      }

      &.ant-radio-button-wrapper-checked {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border-color: transparent;
        color: #ffffff;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
        font-weight: 600;
      }

      &:not(.ant-radio-button-wrapper-checked):hover {
        border-color: #93c5fd;
        background: #eff6ff;
        color: #3b82f6;
      }
    }
  }
}

// 实体弹窗：类型选择按钮样式（全局，保证覆盖 AntD 默认样式）
.entity-modal-form {
  .type-preset-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
  }

  .type-preset-grid .ant-btn {
    width: 100%;
    justify-content: center;
    border-radius: 999px !important;
    height: 40px !important;
    padding: 0 12px;
    border-color: #e2e8f0;
    background: #ffffff;
    color: #475569;
    box-shadow: none;
  }

  .type-preset-grid .ant-btn:not(.ant-btn-primary):hover {
    border-color: #93c5fd;
    color: #1d4ed8;
    background: #eff6ff;
  }

  .type-preset-grid .ant-btn-primary {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    border-color: transparent;
    color: #ffffff;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.35);
  }
}
</style>
