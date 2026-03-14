import re

def fix_alert_level_management():
    file_path = r'd:\hertz_django\hertz_server_django_ui\src\views\admin_page\AlertLevelManagement.vue'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份原文件
    import shutil
    shutil.copy(file_path, file_path + '.bak3')
    
    # 找到script开始的位置
    script_start = content.find('<script setup lang="ts">')
    
    # 找到错误插入CSS的位置 - 在第365行之后
    # 我们需要把内容分成三部分：
    # 1. 正常的JavaScript代码到第367行
    # 2. 错误插入的CSS（需要移除）
    # 3. 应该在style中的CSS
    
    # 让我们用一个更简单的方法：
    # 1. 先找到template结束和script开始
    # 2. 找到正确的script内容应该到哪里
    # 3. 然后添加正确的JavaScript函数
    # 4. 最后添加正确的style标签
    
    # 首先，让我们构建正确的文件结构
    
    # 1. 提取template部分
    template_match = re.search(r'(<template>.*?</template>)', content, re.DOTALL)
    if not template_match:
        print("未找到template")
        return
    template_part = template_match.group(1)
    
    # 2. 提取script部分到第367行（loading.value = true）
    script_content_start = '''<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import {
  WarningOutlined,
  ReloadOutlined,
  EyeOutlined,
  EditOutlined,
  PoweroffOutlined
} from '@ant-design/icons-vue'
import { yoloApi, type AlertLevel, type YoloModel } from '@/api/yolo'
import dayjs from 'dayjs'

// 响应式数据
const loading = ref(false)
const editing = ref(false)
const levels = ref<AlertLevel[]>([])
const searchKeyword = ref('')
const currentModel = ref<YoloModel | null>(null)
const selectedRowKeys = ref<number[]>([])

// 表格多选配置
const rowSelection = computed(() => ({
  selectedRowKeys: selectedRowKeys.value,
  onChange: (keys: (string | number)[]) => {
    selectedRowKeys.value = keys as number[]
  }
}))

// 弹窗状态
const detailModalVisible = ref(false)
const editModalVisible = ref(false)
const currentLevel = ref<AlertLevel | null>(null)
const batchEditModalVisible = ref(false)

// 编辑表单
const editForm = reactive({
  alert_level: 'low' as 'low' | 'medium' | 'high'
})

// 批量编辑表单
const batchEditForm = reactive({
  alert_level: 'low' as 'low' | 'medium' | 'high'
})

// 表单引用
const editFormRef = ref()
const batchEditFormRef = ref()

// 表单验证规则
const editRules = {
  alert_level: [
    { required: true, message: '请选择警告等级', trigger: 'change' }
  ]
}

// 分页配置（受控分页）
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条记录`,
  onChange: (page: number, pageSize: number) => {
    pagination.current = page
    pagination.pageSize = pageSize
  },
  onShowSizeChange: (page: number, pageSize: number) => {
    pagination.current = page
    pagination.pageSize = pageSize
  }
})

// 表格列配置
const columns = [
  {
    title: '名称',
    key: 'name',
    width: 120
  },
  {
    title: '显示名称',
    key: 'display_name',
    width: 150
  },
  {
    title: '别名',
    key: 'alias',
    width: 120
  },
  {
    title: '警告等级',
    key: 'alert_level',
    width: 120
  },
  {
    title: '状态',
    key: 'status',
    width: 100
  },
  {
    title: '操作',
    key: 'actions',
    width: 200
  }
]

// 过滤后的等级列表
const filteredLevels = computed(() => {
  if (!searchKeyword.value) {
    return levels.value
  }
  return levels.value.filter(level => 
    level.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    level.display_name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    level.alert_level_display.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

// 格式化日期
const formatDate = (dateString: string) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm:ss')
}

// 获取警告等级颜色
const getAlertLevelColor = (level: string) => {
  const colorMap = {
    low: 'green',
    medium: 'orange',
    high: 'red'
  }
  return colorMap[level] || 'default'
}

// 获取警告等级列表（仅显示当前启用模型的类别）
const fetchLevels = async () => {
  try {
    loading.value = true
    const response = await yoloApi.getAlertLevels()
    if (response.success && response.data) {
      levels.value = response.data.map(level => ({
        ...level,
        editingAlias: false,
        tempAlias: level.alias
      }))
      pagination.total = levels.value.length
    } else {
      message.error(response.message || '获取警告等级列表失败')
    }
  } catch (error) {
    console.error('获取警告等级列表失败:', error)
    message.error('获取警告等级列表失败')
  } finally {
    loading.value = false
  }
}

// 刷新列表
const refreshLevels = () => {
  fetchLevels()
}

// 编辑警告等级
const editAlertLevel = (record: AlertLevel) => {
  currentLevel.value = record
  editForm.alert_level = record.alert_level
  editModalVisible.value = true
}

// 提交编辑
const handleEditSubmit = async () => {
  if (!currentLevel.value) return
  try {
    const response = await yoloApi.updateAlertLevel(
      String(currentLevel.value.id),
      { alert_level: editForm.alert_level }
    )
    if (response.success) {
      message.success('更新成功')
      editModalVisible.value = false
      fetchLevels()
    } else {
      message.error(response.message || '更新失败')
    }
  } catch (error) {
    console.error('更新警告等级失败:', error)
    message.error('更新失败')
  }
}

// 切换状态
const toggleStatus = async (record: AlertLevel) => {
  try {
    const response = await yoloApi.toggleAlertLevelStatus(String(record.id))
    if (response.success) {
      message.success(record.is_active ? '已禁用' : '已启用')
      fetchLevels()
    } else {
      message.error(response.message || '操作失败')
    }
  } catch (error) {
    console.error('切换状态失败:', error)
    message.error('操作失败')
  }
}

// 开始编辑别名
const startEditAlias = (record: AlertLevel) => {
  record.editingAlias = true
  record.tempAlias = record.alias || ''
  nextTick(() => {
    const inputs = document.querySelectorAll('.alias-input')
    inputs.forEach(input => {
      if (input instanceof HTMLInputElement) {
        input.focus()
      }
    })
  })
}

// 保存别名
const saveAlias = async (record: AlertLevel) => {
  try {
    const response = await yoloApi.updateAlertLevel(
      String(record.id),
      { alias: record.tempAlias || '' }
    )
    if (response.success) {
      record.alias = record.tempAlias || ''
      record.editingAlias = false
      message.success('别名更新成功')
    } else {
      message.error(response.message || '更新失败')
      record.editingAlias = false
    }
  } catch (error) {
    console.error('保存别名失败:', error)
    message.error('更新失败')
    record.editingAlias = false
  }
}

// 取消编辑别名
const cancelEditAlias = (record: AlertLevel) => {
  record.editingAlias = false
  record.tempAlias = record.alias
}

// 搜索
const handleSearch = (value: string) => {
  searchKeyword.value = value
}

// 打开批量编辑
const openBatchEdit = () => {
  batchEditForm.alert_level = 'low'
  batchEditModalVisible.value = true
}

// 批量更新
const handleBatchEditSubmit = async () => {
  try {
    const promises = selectedRowKeys.value.map(id => 
      yoloApi.updateAlertLevel(String(id), { alert_level: batchEditForm.alert_level })
    )
    await Promise.all(promises)
    message.success('批量更新成功')
    batchEditModalVisible.value = false
    selectedRowKeys.value = []
    fetchLevels()
  } catch (error) {
    console.error('批量更新失败:', error)
    message.error('批量更新失败')
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchLevels()
})
</script>'''

    # 3. 提取正确的style部分（从第368行开始到结尾的CSS代码）
    # 我们需要找到原来错误插入的CSS并把它放到正确的位置
    # 让我们从原内容中提取CSS部分
    style_content = '''<style scoped lang="scss">
.alert-level-management {
  min-height: 100vh;
  
  // 页面头部 - 苹果风格
  .page-header {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(245, 250, 255, 0.92) 30%, rgba(235, 245, 255, 0.88) 100%);
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
        background: rgba(245, 158, 11, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        color: #f59e0b;
        font-size: 24px;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        
        &:hover {
          transform: scale(1.05);
          background: rgba(245, 158, 11, 0.15);
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

  // 操作栏 - 苹果风格
  .action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 0 28px 24px 28px;
    padding: 20px 24px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.92) 0%, rgba(245, 250, 255, 0.88) 50%, rgba(235, 245, 255, 0.84) 100%);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 212, 255, 0.08), 0 2px 8px rgba(0, 0, 0, 0.04);
    border: 1px solid rgba(0, 212, 255, 0.2);
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    flex-wrap: wrap;
    gap: 16px;
    
    &:hover {
      box-shadow: 0 8px 30px rgba(0, 212, 255, 0.2), 0 4px 12px rgba(0, 0, 0, 0.08);
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
        border-color: rgba(0, 0, 0, 0.12);
        color: #1d1d1f;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.92) 0%, rgba(245, 250, 255, 0.88) 50%, rgba(235, 245, 255, 0.84) 100%);
        
        &:hover {
          background: rgba(0, 0, 0, 0.04);
          border-color: rgba(0, 0, 0, 0.16);
          transform: translateY(-1px);
        }
      }
    }
    
    .action-right {
      display: flex;
      align-items: center;
      
      :deep(.ant-input-search) {
        .ant-input {
          border-radius: 10px;
          border: 1px solid rgba(0, 212, 255, 0.25);
          background: linear-gradient(135deg, rgba(255, 255, 255, 0.92) 0%, rgba(245, 250, 255, 0.88) 50%, rgba(235, 245, 255, 0.84) 100%);
          transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
          height: 40px;
          
          &:hover {
            border-color: #00d4ff;
          }
          
          &:focus {
            border-color: #00d4ff;
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
  .levels-table {
    margin: 0 28px 24px 28px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.92) 0%, rgba(245, 250, 255, 0.88) 50%, rgba(235, 245, 255, 0.84) 100%);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 212, 255, 0.08), 0 2px 8px rgba(0, 0, 0, 0.04);
    border: 1px solid rgba(0, 212, 255, 0.2);
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    
    &:hover {
      box-shadow: 0 8px 30px rgba(0, 212, 255, 0.2), 0 4px 12px rgba(0, 0, 0, 0.08);
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
    
    .alias-cell {
      .alias-display {
        cursor: pointer;
        padding: 8px 12px;
        border-radius: 10px;
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-width: 100px;
        border: 0.5px dashed rgba(0, 0, 0, 0.12);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.92) 0%, rgba(245, 250, 255, 0.88) 50%, rgba(235, 245, 255, 0.84) 100%);
        backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px);
        position: relative;
        
        &:hover {
          border-color: #00d4ff;
          background: rgba(255, 255, 255, 1);
          transform: translateY(-1px);
          box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
          
          .alias-text {
            color: #3b82f6;
            font-weight: 500;
          }
          
          .edit-icon {
            color: #3b82f6;
            transform: scale(1.1);
          }
        }
        
        .alias-text {
          color: #1d1d1f;
          font-size: 13px;
          transition: all 0.2s ease;
          flex: 1;
          
          &:empty::before {
            content: '点击编辑';
            color: #86868b;
            font-style: italic;
          }
        }
        
        .edit-icon {
          color: #86868b;
          font-size: 12px;
          margin-left: 6px;
          transition: all 0.2s ease;
        }
      }
      
      .alias-input {
        border: 0.5px solid #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        border-radius: 10px !important;
        background: rgba(255, 255, 255, 1) !important;
        
        &:focus {
          border-color: #00d4ff !important;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
        }
      }
    }
    
    // 标签样式优化
    :deep(.ant-tag) {
      border-radius: 6px;
      font-weight: 500;
      padding: 2px 10px;
      border: 0.5px solid currentColor;
      opacity: 0.8;
    }
  }

  .level-detail {
    :deep(.ant-descriptions-item-label) {
      font-weight: 500;
      color: #1d1d1f;
      background: rgba(0, 0, 0, 0.02);
    }
    
    :deep(.ant-descriptions-item-content) {
      color: #86868b;
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
      border: 1px solid rgba(0, 212, 255, 0.25);
      margin: 0 4px;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.92) 0%, rgba(245, 250, 255, 0.88) 50%, rgba(235, 245, 255, 0.84) 100%);
      transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      
      &:hover {
        border-color: #00d4ff;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
      }
      
      &.ant-pagination-item-active {
        background: #3b82f6;
        border-color: #00d4ff;
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
      border: 1px solid rgba(0, 212, 255, 0.25);
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.92) 0%, rgba(245, 250, 255, 0.88) 50%, rgba(235, 245, 255, 0.84) 100%);
      transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      
      &:hover {
        border-color: #00d4ff;
        color: #3b82f6;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
      }
    }
    
    .ant-select {
      margin: 0 8px;
      
      .ant-select-selector {
        border-radius: 8px;
        border: 1px solid rgba(0, 212, 255, 0.25);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.92) 0%, rgba(245, 250, 255, 0.88) 50%, rgba(235, 245, 255, 0.84) 100%);
        transition: all 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        
        &:hover {
          border-color: #00d4ff;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .alert-level-management {
    .page-header,
    .action-bar,
    .levels-table {
      margin-left: 20px;
      margin-right: 20px;
    }
  }
}

@media (max-width: 768px) {
  .alert-level-management {
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
    
    .levels-table {
      margin: 0 16px 20px 16px;
      border-radius: 12px;
    }
  }
}
</style>'''

    # 组合完整文件
    new_content = template_part + '\n\n' + script_content_start + '\n\n' + style_content
    
    # 写入修复后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("AlertLevelManagement.vue 修复完成！原文件已备份为 .bak3")

if __name__ == '__main__':
    fix_alert_level_management()
