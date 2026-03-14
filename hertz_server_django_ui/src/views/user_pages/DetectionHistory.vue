<template>
  <div class="detection-history-page">
    <div class="page-header">
      <h1 class="page-title">
        <HistoryOutlined class="title-icon" />
        检测历史记录
      </h1>
      <p class="page-description">查看和管理您的检测历史记录</p>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <a-row :gutter="16" align="middle">
        <a-col :span="6">
          <a-input-search
            v-model:value="searchKeyword"
            placeholder="搜索文件名或检测结果"
            @search="handleSearch"
            allowClear
          />
        </a-col>
        <a-col :span="4">
          <a-select
            v-model:value="filterClass"
            placeholder="选择检测类别"
            allowClear
            @change="handleFilter"
          >
            <a-select-option value="">全部类别</a-select-option>
            <a-select-option value="person">人员</a-select-option>
            <a-select-option value="car">车辆</a-select-option>
            <a-select-option value="dog">狗</a-select-option>
            <a-select-option value="cat">猫</a-select-option>
            <a-select-option value="bicycle">自行车</a-select-option>
          </a-select>
        </a-col>
        <a-col :span="4">
          <a-range-picker
            v-model:value="dateRange"
            @change="handleDateFilter"
            format="YYYY-MM-DD"
          />
        </a-col>
        <a-col :span="4">
          <a-button @click="resetFilters">
            <ReloadOutlined />
            重置筛选
          </a-button>
        </a-col>
        <a-col :span="6" style="text-align: right">
          <a-space>
            <a-checkbox
              v-if="detectionHistory.length > 0"
              :checked="isAllSelected"
              :indeterminate="isIndeterminate"
              @change="handleSelectAll"
            >
              全选
            </a-checkbox>
            <a-button
              danger
              @click="batchDeleteRecords"
              :loading="batchDeleting"
              :disabled="selectedRecordIds.length === 0"
            >
              <DeleteOutlined />
              批量删除{{ selectedRecordIds.length > 0 ? ` (${selectedRecordIds.length})` : '' }}
            </a-button>
            <a-button type="primary" @click="exportHistory">
              <DownloadOutlined />
              导出记录
            </a-button>
          </a-space>
        </a-col>
      </a-row>
    </div>

    <!-- 历史记录列表 -->
    <div class="history-content">
      <a-spin :spinning="loading">
        <div v-if="detectionHistory.length === 0" class="no-data">
          <div class="no-data-icon">
            <FileTextOutlined />
          </div>
          <p>暂无检测记录</p>
          <p class="no-data-hint">开始使用YOLO检测功能来创建记录</p>
        </div>

        <!-- 布局1：网格布局（默认） -->
        <div
          v-else-if="currentLayout === 'default'"
          :key="`grid-${layoutKey}`"
          class="history-grid"
        >
          <div
            v-for="record in detectionHistory"
            :key="record.id"
            class="history-item"
            @click="viewDetails(record)"
          >
            <div class="item-card">
              <!-- 选择复选框 -->
              <div class="item-checkbox">
                <a-checkbox
                  :checked="selectedRecordIds.includes(record.id)"
                  @change="(e) => handleRecordSelect(record.id, e.target.checked)"
                  @click.stop
                />
              </div>
              <!-- 媒体预览区域 -->
              <div class="media-section">
                <div class="media-container">
                  <div
                    v-if="record.detection_type === 'video'"
                    class="media-thumbnail video-thumbnail"
                  >
                    <video
                      :src="getFullFileUrl(record.original_file)"
                      preload="metadata"
                      muted
                    ></video>
                    <div class="media-overlay">
                      <div class="play-icon">
                        <PlayCircleOutlined />
                      </div>
                      <div class="overlay-stats">
                        <div class="stat-item">
                          <span class="stat-number">{{
                            record.object_count || record.detections.length
                          }}</span>
                          <span class="stat-label">目标</span>
                        </div>
                        <div class="stat-item">
                          <span class="stat-number">{{ record.processing_time }}ms</span>
                          <span class="stat-label">耗时</span>
                        </div>
                      </div>
                    </div>
                    <div class="media-type-badge video-badge">
                      <VideoCameraOutlined />
                    </div>
                  </div>
                  <div v-else class="media-thumbnail image-thumbnail">
                    <img
                      :src="getFullFileUrl(record.original_file)"
                      :alt="record.filename"
                      @error="handleImageError"
                    />
                    <div class="media-overlay">
                      <div class="overlay-stats">
                        <div class="stat-item">
                          <span class="stat-number">{{
                            record.object_count || record.detections.length
                          }}</span>
                          <span class="stat-label">目标</span>
                        </div>
                        <div class="stat-item">
                          <span class="stat-number">{{ record.processing_time }}ms</span>
                          <span class="stat-label">耗时</span>
                        </div>
                      </div>
                    </div>
                    <div class="media-type-badge image-badge">
                      <FileImageOutlined />
                    </div>
                  </div>
                </div>
              </div>

              <!-- 信息区域 -->
              <div class="info-section">
                <div class="item-header">
                  <div class="file-info">
                    <h3 class="item-title">{{ record.filename }}</h3>
                    <div class="item-meta">
                      <span class="meta-item">
                        <ClockCircleOutlined />
                        {{ formatDate(new Date(record.created_at)) }}
                      </span>
                      <span class="meta-item">
                        <ScanOutlined />
                        {{ record.model_name }}
                      </span>
                    </div>
                  </div>
                  <div class="item-actions">
                    <a-button
                      size="small"
                      type="primary"
                      @click.stop="viewDetails(record)"
                      class="action-btn"
                    >
                      <EyeOutlined />
                      查看详情
                    </a-button>
                    <a-popconfirm title="确定要删除这条记录吗？" @confirm="deleteRecord(record.id)">
                      <a-button size="small" danger @click.stop class="action-btn">
                        <DeleteOutlined />
                        删除
                      </a-button>
                    </a-popconfirm>
                  </div>
                </div>

                <div class="detection-results">
                  <div class="results-header">
                    <span class="results-title">检测结果</span>
                    <span class="results-count">{{ record.detections.length }} 个目标</span>
                  </div>
                  <div class="result-tags">
                    <a-tag
                      v-for="(detection, index) in record.detections.slice(0, 4)"
                      :key="index"
                      :color="getTagColor(detection.class)"
                      class="result-tag"
                    >
                      {{ detection.class }} ({{ (detection.confidence * 100).toFixed(1) }}%)
                    </a-tag>
                    <a-tag v-if="record.detections.length > 4" class="more-tag">
                      +{{ record.detections.length - 4 }}
                    </a-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 布局2：列表布局 -->
        <div
          v-else-if="currentLayout === 'list'"
          :key="`list-${layoutKey}`"
          class="history-list-layout"
        >
          <div
            v-for="record in detectionHistory"
            :key="record.id"
            class="history-item-list"
            @click="viewDetails(record)"
          >
            <div class="item-card-list">
              <!-- 选择复选框 -->
              <div class="item-checkbox-list">
                <a-checkbox
                  :checked="selectedRecordIds.includes(record.id)"
                  @change="(e) => handleRecordSelect(record.id, e.target.checked)"
                  @click.stop
                />
              </div>
              <!-- 左侧：媒体预览 -->
              <div class="media-section-list">
                <div class="media-container-list">
                  <div
                    v-if="record.detection_type === 'video'"
                    class="media-thumbnail-list video-thumbnail"
                  >
                    <video
                      :src="getFullFileUrl(record.original_file)"
                      preload="metadata"
                      muted
                    ></video>
                    <div class="media-overlay-list">
                      <div class="play-icon">
                        <PlayCircleOutlined />
                      </div>
                      <div class="overlay-stats-list">
                        <div class="stat-item">
                          <span class="stat-number">{{
                            record.object_count || record.detections.length
                          }}</span>
                          <span class="stat-label">目标</span>
                        </div>
                        <div class="stat-item">
                          <span class="stat-number">{{ record.processing_time }}ms</span>
                          <span class="stat-label">耗时</span>
                        </div>
                      </div>
                    </div>
                    <div class="media-type-badge video-badge">
                      <VideoCameraOutlined />
                    </div>
                  </div>
                  <div v-else class="media-thumbnail-list image-thumbnail">
                    <img
                      :src="getFullFileUrl(record.original_file)"
                      :alt="record.filename"
                      @error="handleImageError"
                    />
                    <div class="media-overlay-list">
                      <div class="overlay-stats-list">
                        <div class="stat-item">
                          <span class="stat-number">{{
                            record.object_count || record.detections.length
                          }}</span>
                          <span class="stat-label">目标</span>
                        </div>
                        <div class="stat-item">
                          <span class="stat-number">{{ record.processing_time }}ms</span>
                          <span class="stat-label">耗时</span>
                        </div>
                      </div>
                    </div>
                    <div class="media-type-badge image-badge">
                      <FileImageOutlined />
                    </div>
                  </div>
                </div>
              </div>

              <!-- 中间：信息区域 -->
              <div class="info-section-list">
                <div class="item-header-list">
                  <div class="file-info-list">
                    <h3 class="item-title-list">{{ record.filename }}</h3>
                    <div class="item-meta-list">
                      <span class="meta-item">
                        <ClockCircleOutlined />
                        {{ formatDate(new Date(record.created_at)) }}
                      </span>
                      <span class="meta-item">
                        <ScanOutlined />
                        {{ record.model_name }}
                      </span>
                    </div>
                  </div>
                  <div class="item-actions-list">
                    <a-button
                      size="small"
                      type="primary"
                      @click.stop="viewDetails(record)"
                      class="action-btn"
                    >
                      <EyeOutlined />
                      查看详情
                    </a-button>
                    <a-popconfirm title="确定要删除这条记录吗？" @confirm="deleteRecord(record.id)">
                      <a-button size="small" danger @click.stop class="action-btn">
                        <DeleteOutlined />
                        删除
                      </a-button>
                    </a-popconfirm>
                  </div>
                </div>
                <div class="detection-results-list">
                  <div class="results-header-list">
                    <span class="results-title">检测结果</span>
                    <span class="results-count">{{ record.detections.length }} 个目标</span>
                  </div>
                  <div class="result-tags">
                    <a-tag
                      v-for="(detection, index) in record.detections.slice(0, 6)"
                      :key="index"
                      :color="getTagColor(detection.class)"
                      class="result-tag"
                    >
                      {{ detection.class }} ({{ (detection.confidence * 100).toFixed(1) }}%)
                    </a-tag>
                    <a-tag v-if="record.detections.length > 6" class="more-tag">
                      +{{ record.detections.length - 6 }}
                    </a-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 布局3：卡片流布局 -->
        <div v-else-if="currentLayout === 'flow'" :key="`flow-${layoutKey}`" class="history-flow">
          <div
            v-for="record in detectionHistory"
            :key="record.id"
            class="history-item-flow"
            @click="viewDetails(record)"
          >
            <div class="item-card-flow">
              <!-- 选择复选框 -->
              <div class="item-checkbox-flow">
                <a-checkbox
                  :checked="selectedRecordIds.includes(record.id)"
                  @change="(e) => handleRecordSelect(record.id, e.target.checked)"
                  @click.stop
                />
              </div>
              <!-- 媒体预览区域 -->
              <div class="media-section-flow">
                <div class="media-container-flow">
                  <div
                    v-if="record.detection_type === 'video'"
                    class="media-thumbnail-flow video-thumbnail"
                  >
                    <video
                      :src="getFullFileUrl(record.original_file)"
                      preload="metadata"
                      muted
                    ></video>
                    <div class="media-overlay-flow">
                      <div class="play-icon">
                        <PlayCircleOutlined />
                      </div>
                      <div class="overlay-stats-flow">
                        <div class="stat-item">
                          <span class="stat-number">{{
                            record.object_count || record.detections.length
                          }}</span>
                          <span class="stat-label">目标</span>
                        </div>
                      </div>
                    </div>
                    <div class="media-type-badge video-badge">
                      <VideoCameraOutlined />
                    </div>
                  </div>
                  <div v-else class="media-thumbnail-flow image-thumbnail">
                    <img
                      :src="getFullFileUrl(record.original_file)"
                      :alt="record.filename"
                      @error="handleImageError"
                    />
                    <div class="media-overlay-flow">
                      <div class="overlay-stats-flow">
                        <div class="stat-item">
                          <span class="stat-number">{{
                            record.object_count || record.detections.length
                          }}</span>
                          <span class="stat-label">目标</span>
                        </div>
                      </div>
                    </div>
                    <div class="media-type-badge image-badge">
                      <FileImageOutlined />
                    </div>
                  </div>
                </div>
              </div>

              <!-- 信息区域 -->
              <div class="info-section-flow">
                <h3 class="item-title-flow">{{ record.filename }}</h3>
                <div class="item-meta-flow">
                  <span class="meta-item">
                    <ClockCircleOutlined />
                    {{ formatDate(new Date(record.created_at)) }}
                  </span>
                </div>
                <div class="detection-results-flow">
                  <div class="result-tags">
                    <a-tag
                      v-for="(detection, index) in record.detections.slice(0, 3)"
                      :key="index"
                      :color="getTagColor(detection.class)"
                      class="result-tag"
                    >
                      {{ detection.class }}
                    </a-tag>
                    <a-tag v-if="record.detections.length > 3" class="more-tag">
                      +{{ record.detections.length - 3 }}
                    </a-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="totalRecords > 0" class="pagination-wrapper">
          <a-pagination
            v-model:current="currentPage"
            v-model:page-size="pageSize"
            :total="totalRecords"
            :show-size-changer="true"
            :show-quick-jumper="true"
            :show-total="(total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`"
            @change="handlePageChange"
            @show-size-change="handlePageSizeChange"
          />
        </div>
      </a-spin>
    </div>

    <!-- 详情模态框 -->
    <a-modal
      v-model:visible="detailModalVisible"
      title="检测详情"
      width="1200px"
      :footer="null"
      :z-index="1000"
      :mask-closable="true"
      :centered="true"
      :destroy-on-close="false"
      @cancel="closeDetailModal"
    >
      <a-spin :spinning="detailLoading" tip="正在加载详情...">
        <div class="detail-content">
          <div v-if="selectedRecord" class="detail-layout">
            <!-- 左侧：媒体文件展示 -->
            <div class="detail-left">
              <div
                class="detail-media"
                style="display: flex; flex-direction: row; gap: 12px; align-items: flex-start"
              >
                <div class="media-item" style="flex: 1; text-align: center; min-width: 0">
                  <h5 style="margin-bottom: 8px; font-size: 14px">原文件</h5>
                  <!-- 视频播放器 -->
                  <div
                    v-if="selectedRecord.detection_type === 'video'"
                    style="width: 100%; max-width: 100%; overflow: hidden; position: relative"
                  >
                    <video
                      :src="getFullFileUrl(selectedRecord.original_file)"
                      controls
                      preload="metadata"
                      style="
                        width: 100%;
                        max-height: 150px;
                        border-radius: 8px;
                        object-fit: contain;
                      "
                      @error="handleVideoError"
                      @loadstart="handleVideoLoadStart"
                    >
                      您的浏览器不支持视频播放
                    </video>
                    <div style="position: absolute; top: 8px; right: 8px">
                      <a-button
                        size="small"
                        type="primary"
                        @click="openVideoInNewTab(selectedRecord.original_file)"
                        style="opacity: 0.8"
                      >
                        <EyeOutlined />
                        全屏查看
                      </a-button>
                    </div>
                    <div style="margin-top: 8px">
                      <a-button
                        size="small"
                        @click="
                          downloadVideo(
                            selectedRecord.original_file,
                            selectedRecord.original_filename
                          )
                        "
                      >
                        <DownloadOutlined />
                        下载原视频
                      </a-button>
                    </div>
                  </div>
                  <!-- 图片显示 -->
                  <div v-else style="width: 100%; max-width: 100%; overflow: hidden">
                    <div
                      style="
                        width: 100%;
                        max-height: 150px;
                        border: 2px dashed #d9d9d9;
                        border-radius: 8px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        background: #fafafa;
                        overflow: hidden;
                        position: relative;
                      "
                    >
                      <a-image
                        :src="getFullFileUrl(selectedRecord.original_file)"
                        :alt="selectedRecord.original_filename"
                        style="
                          max-width: 100%;
                          max-height: 100%;
                          object-fit: contain;
                          width: 100%;
                          height: auto;
                          cursor: pointer;
                          border-radius: 4px;
                        "
                        :preview="{
                          mask: '点击放大',
                          zIndex: 10002,
                          onVisibleChange: handleImagePreview,
                        }"
                        @error="handleImageError"
                        @load="handleImageLoad"
                      />
                      <div
                        style="
                          position: absolute;
                          top: 4px;
                          left: 4px;
                          background: rgba(0, 0, 0, 0.6);
                          color: white;
                          padding: 2px 6px;
                          border-radius: 4px;
                          font-size: 12px;
                          pointer-events: none;
                        "
                      >
                        <EyeOutlined /> 点击放大
                      </div>
                    </div>
                    <div style="margin-top: 8px">
                      <a-button
                        size="small"
                        @click="
                          downloadImage(
                            selectedRecord.original_file,
                            selectedRecord.original_filename
                          )
                        "
                      >
                        <DownloadOutlined />
                        下载原图
                      </a-button>
                      <a-button
                        size="small"
                        @click="openImageInNewTab(selectedRecord.original_file)"
                        style="margin-left: 8px"
                      >
                        <EyeOutlined />
                        新窗口查看
                      </a-button>
                    </div>
                  </div>
                </div>
                <div class="media-item" style="flex: 1; text-align: center; min-width: 0">
                  <h5 style="margin-bottom: 8px; font-size: 14px">检测结果</h5>
                  <!-- 视频播放器 -->
                  <div
                    v-if="selectedRecord.detection_type === 'video'"
                    style="width: 100%; max-width: 100%; overflow: hidden; position: relative"
                  >
                    <video
                      :src="getFullFileUrl(selectedRecord.result_file)"
                      controls
                      preload="metadata"
                      style="
                        width: 100%;
                        max-height: 150px;
                        border-radius: 8px;
                        object-fit: contain;
                      "
                      @error="handleVideoError"
                      @loadstart="handleVideoLoadStart"
                    >
                      您的浏览器不支持视频播放
                    </video>
                    <div style="position: absolute; top: 8px; right: 8px">
                      <a-button
                        size="small"
                        type="primary"
                        @click="openVideoInNewTab(selectedRecord.result_file)"
                        style="opacity: 0.8"
                      >
                        <EyeOutlined />
                        全屏查看
                      </a-button>
                    </div>
                    <div style="margin-top: 8px">
                      <a-button
                        size="small"
                        @click="
                          downloadVideo(selectedRecord.result_file, selectedRecord.result_filename)
                        "
                      >
                        <DownloadOutlined />
                        下载结果视频
                      </a-button>
                    </div>
                  </div>
                  <!-- 图片显示 -->
                  <div v-else style="width: 100%; max-width: 100%; overflow: hidden">
                    <div
                      style="
                        width: 100%;
                        max-height: 150px;
                        border: 2px dashed #d9d9d9;
                        border-radius: 8px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        background: #fafafa;
                        overflow: hidden;
                        position: relative;
                      "
                    >
                      <a-image
                        :src="getFullFileUrl(selectedRecord.result_file)"
                        :alt="selectedRecord.result_filename"
                        style="
                          max-width: 100%;
                          max-height: 100%;
                          object-fit: contain;
                          width: 100%;
                          height: auto;
                          cursor: pointer;
                          border-radius: 4px;
                        "
                        :preview="{
                          mask: '点击放大',
                          zIndex: 10002,
                          onVisibleChange: handleImagePreview,
                        }"
                        @error="handleImageError"
                        @load="handleImageLoad"
                      />
                      <div
                        style="
                          position: absolute;
                          top: 4px;
                          left: 4px;
                          background: rgba(0, 0, 0, 0.6);
                          color: white;
                          padding: 2px 6px;
                          border-radius: 4px;
                          font-size: 12px;
                          pointer-events: none;
                        "
                      >
                        <EyeOutlined /> 点击放大
                      </div>
                    </div>
                    <div style="margin-top: 8px">
                      <a-button
                        size="small"
                        @click="
                          downloadImage(selectedRecord.result_file, selectedRecord.result_filename)
                        "
                      >
                        <DownloadOutlined />
                        下载结果图
                      </a-button>
                      <a-button
                        size="small"
                        @click="openImageInNewTab(selectedRecord.result_file)"
                        style="margin-left: 8px"
                      >
                        <EyeOutlined />
                        新窗口查看
                      </a-button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 右侧：详细信息 -->
            <div class="detail-right">
              <div class="detail-info">
                <h4>{{ selectedRecord.filename }}</h4>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="info-label">检测时间：</span>
                    <span class="info-value">{{
                      formatDate(new Date(selectedRecord.created_at))
                    }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">检测目标数：</span>
                    <span class="info-value"
                      >{{
                        selectedRecord.object_count || selectedRecord.detections.length
                      }}
                      个</span
                    >
                  </div>
                  <div class="info-item">
                    <span class="info-label">处理时间：</span>
                    <span class="info-value">{{ selectedRecord.processing_time }}ms</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">模型：</span>
                    <span class="info-value">{{ selectedRecord.model_name }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">文件类型：</span>
                    <span class="info-value">{{
                      selectedRecord.detection_type === 'image' ? '图片' : '视频'
                    }}</span>
                  </div>
                  <div class="info-item" v-if="selectedRecord.avg_confidence">
                    <span class="info-label">平均置信度：</span>
                    <span class="info-value"
                      >{{ (selectedRecord.avg_confidence * 100).toFixed(1) }}%</span
                    >
                  </div>
                </div>
              </div>

              <div class="detail-detections">
                <h5>检测结果详情：</h5>
                <div class="detection-table">
                  <template
                    v-if="
                      selectedRecord.detected_categories &&
                      selectedRecord.detected_categories.length > 0
                    "
                  >
                    <a-table
                      :columns="detectionColumns"
                      :data-source="selectedRecord.detections"
                      :pagination="false"
                      size="small"
                    />
                  </template>
                  <template v-else>
                    <p>未检测到任何目标</p>
                  </template>
                </div>
              </div>
            </div>
          </div>

          <!-- 关闭按钮 -->
          <div
            style="
              text-align: center;
              margin-top: 20px;
              padding-top: 20px;
              border-top: 1px solid #f0f0f0;
            "
          >
            <a-button type="primary" @click="closeDetailModal">关闭</a-button>
          </div>
        </div>
      </a-spin>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick, h } from 'vue';
import { message, Image, Modal } from 'ant-design-vue';
import {
  HistoryOutlined,
  ClockCircleOutlined,
  ScanOutlined,
  AimOutlined,
  EyeOutlined,
  DownloadOutlined,
  DeleteOutlined,
  ReloadOutlined,
  FileTextOutlined,
  PlayCircleOutlined,
  VideoCameraOutlined,
  FileImageOutlined,
} from '@ant-design/icons-vue';
import { detectionHistoryApi, type DetectionHistoryRecord } from '@/api/yolo';
import { useUserStore } from '@/stores/hertz_user';
import { getFullFileUrl } from '@/utils/hertz_url';

// 响应式数据
const loading = ref(false);
const searchKeyword = ref('');
const filterClass = ref('');
const dateRange = ref([]);
const currentPage = ref(1);
const pageSize = ref(10);
const detailModalVisible = ref(false);
const selectedRecord = ref<DetectionHistoryRecord | null>(null);
const detailLoading = ref(false);
const userStore = useUserStore();

// 批量选择和删除
const selectedRecordIds = ref<string[]>([]);
const batchDeleting = ref(false);

// 检测历史布局配置
const detectionHistoryLayouts = [
  {
    name: 'default',
    label: '网格布局',
    description: '两列网格布局，卡片式展示，适合快速浏览和对比',
    cardClass: 'card-grid',
  },
  {
    name: 'list',
    label: '列表布局',
    description: '垂直列表布局，紧凑显示详细信息，适合详细查看',
    cardClass: 'card-list',
  },
  {
    name: 'flow',
    label: '卡片流布局',
    description: '瀑布流式卡片布局，全屏展示，适合大量记录浏览',
    cardClass: 'card-flow',
  },
];

// 当前布局
const currentLayout = ref<string>('default');
// 布局切换的key，用于强制重新渲染
const layoutKey = ref(0);

// 加载布局配置
const loadLayout = () => {
  const savedLayout = localStorage.getItem('detectionHistoryLayout');
  if (savedLayout && detectionHistoryLayouts.find((l) => l.name === savedLayout)) {
    currentLayout.value = savedLayout;
  } else {
    currentLayout.value = 'default';
  }
  // 强制更新布局key
  layoutKey.value++;
};

// 监听布局变化事件
const handleLayoutChange = async () => {
  loadLayout();
  // 等待DOM更新
  await nextTick();
};

// 监听currentLayout变化，确保立即响应
watch(
  currentLayout,
  async (newLayout, oldLayout) => {
    if (newLayout !== oldLayout) {
      // 布局切换时强制更新
      await nextTick();
      layoutKey.value++;
    }
  },
  { immediate: false }
);

// 检测记录接口
interface Detection {
  class: string;
  confidence: number;
  bbox: [number, number, number, number];
}

interface DetectionRecord {
  id: string;
  filename: string;
  imageUrl: string;
  detectionTime: Date;
  detections: Detection[];
  averageConfidence: number;
}

// 检测历史数据
const detectionHistory = ref<DetectionHistoryRecord[]>([]);
const totalRecords = ref(0);

// 加载检测历史数据
const loadDetectionHistory = async () => {
  if (!userStore.userInfo?.user_id) {
    message.error('用户信息不存在，请重新登录');
    return;
  }

  loading.value = true;
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchKeyword.value || undefined,
      class_filter: filterClass.value || undefined,
      start_date: dateRange.value?.[0]?.format('YYYY-MM-DD'),
      end_date: dateRange.value?.[1]?.format('YYYY-MM-DD'),
    };

    console.log('🔍 加载检测历史，参数:', params);

    const response = await detectionHistoryApi.getUserDetectionHistory(
      userStore.userInfo.user_id,
      params
    );

    console.log('📊 检测历史响应:', response);
    console.log('📊 响应类型:', typeof response);
    console.log('📊 响应键:', Object.keys(response));
    console.log('📊 response.success:', response.success);
    console.log('📊 response.data:', response.data);
    console.log('📊 response.message:', response.message);

    // 处理不同的响应结构
    let rawData: any[] = [];

    if (response.success && response.data && response.data.records) {
      console.log('📊 标准格式响应');
      rawData = response.data.records;
      totalRecords.value = response.data.total || 0;
    } else if (response.data && Array.isArray(response.data)) {
      console.log('📊 直接返回数组结构');
      rawData = response.data;
      totalRecords.value = response.data.length;
    } else if (response.results && Array.isArray(response.results)) {
      console.log('📊 使用results字段');
      rawData = response.results;
      totalRecords.value = response.count || response.results.length;
    } else if (Array.isArray(response)) {
      console.log('📊 响应本身就是数组');
      rawData = response;
      totalRecords.value = response.length;
    } else {
      console.error('❌ 检测历史加载失败 - 未知响应结构:', response);
      message.error('加载检测历史失败 - 响应格式不正确');
      return;
    }

    // 转换数据格式以匹配前端显示
    detectionHistory.value = rawData.map((record) => {
      // 构建检测结果数组
      const detections: any[] = [];
      if (record.detected_categories && record.confidence_scores) {
        for (let i = 0; i < record.detected_categories.length; i++) {
          detections.push({
            class_name: record.detected_categories[i],
            confidence: record.confidence_scores[i] || 0,
            bbox: { x: 0, y: 0, width: 0, height: 0 }, // 后端没有返回bbox信息
          });
        }
      }

      return {
        ...record,
        // 添加前端需要的字段
        filename: record.original_filename || record.result_filename || '未知文件',
        image_url: record.result_file || record.original_file || '',
        detections: detections,
        // 确保有默认值
        object_count: record.object_count || 0,
        detected_categories: record.detected_categories || [],
        confidence_scores: record.confidence_scores || [],
        avg_confidence: record.avg_confidence || 0,
      };
    });

    console.log('✅ 检测历史加载成功:', detectionHistory.value.length, '条记录');
    console.log('📊 处理后的数据:', detectionHistory.value);
  } catch (error) {
    console.error('❌ 检测历史加载异常:', error);
    message.error('加载检测历史失败，请检查网络连接');
  } finally {
    loading.value = false;
  }
};

// 检测详情表格列
const detectionColumns = [
  {
    title: '类别',
    dataIndex: 'class_name',
    key: 'class_name',
    customRender: ({ text }: { text: string }) => {
      return h('a-tag', { color: getDetectionColor(text) }, text);
    },
  },
  {
    title: '置信度',
    dataIndex: 'confidence',
    key: 'confidence',
    customRender: ({ text }: { text: number }) => `${(text * 100).toFixed(1)}%`,
  },
  {
    title: '边界框',
    dataIndex: 'bbox',
    key: 'bbox',
    customRender: ({ text }: { text: { x: number; y: number; width: number; height: number } }) =>
      `[${text.x}, ${text.y}, ${text.width}, ${text.height}]`,
  },
];

// 计算属性

// 方法
const handleSearch = () => {
  currentPage.value = 1;
  selectedRecordIds.value = []; // 搜索时清空选择
  loadDetectionHistory();
};

const handleFilter = () => {
  currentPage.value = 1;
  selectedRecordIds.value = []; // 筛选时清空选择
  loadDetectionHistory();
};

const handleDateFilter = () => {
  currentPage.value = 1;
  selectedRecordIds.value = []; // 日期筛选时清空选择
  loadDetectionHistory();
};

const resetFilters = () => {
  searchKeyword.value = '';
  filterClass.value = '';
  dateRange.value = [];
  currentPage.value = 1;
  selectedRecordIds.value = []; // 重置筛选时清空选择
  loadDetectionHistory();
};

const handlePageChange = (page: number) => {
  currentPage.value = page;
  selectedRecordIds.value = []; // 切换页面时清空选择
  loadDetectionHistory();
};

const handlePageSizeChange = (current: number, size: number) => {
  currentPage.value = 1;
  pageSize.value = size;
  selectedRecordIds.value = []; // 切换页面大小时清空选择
  loadDetectionHistory();
};

const viewDetails = async (record: DetectionHistoryRecord) => {
  console.log('🔍 查看详情函数被调用，记录ID:', record.id);

  try {
    // 立即显示模态框
    selectedRecord.value = record;
    detailModalVisible.value = true;
    detailLoading.value = true;

    console.log('📱 模态框状态已设置:', {
      detailModalVisible: detailModalVisible.value,
      selectedRecord: selectedRecord.value?.id,
    });

    // 获取详细信息
    const response = await detectionHistoryApi.getDetectionRecordDetail(record.id);
    console.log('📊 详情响应:', response);

    // 检查不同的响应结构
    let detailData = null;

    if (response.success && response.data) {
      detailData = response.data;
    } else if (response.data && !response.success) {
      detailData = response.data;
    } else {
      console.error('❌ 获取详情失败 - 响应结构不匹配:', response);
      message.error(response.message || '获取详情失败 - 响应格式不正确');
      return;
    }

    if (detailData) {
      // 转换数据格式以匹配前端显示
      const detailRecord = {
        ...detailData,
        // 添加前端需要的字段
        filename: detailData.original_filename || detailData.result_filename || '未知文件',
        image_url: detailData.result_file || detailData.original_file || '',
        // 构建检测结果数组
        detections:
          detailData.detected_categories?.map((category: string, index: number) => ({
            class_name: category,
            confidence: detailData.confidence_scores?.[index] || 0,
            bbox: { x: 0, y: 0, width: 0, height: 0 },
          })) || [],
        // 确保有默认值
        object_count: detailData.object_count || 0,
        detected_categories: detailData.detected_categories || [],
        confidence_scores: detailData.confidence_scores || [],
        avg_confidence: detailData.avg_confidence || 0,
      };

      selectedRecord.value = detailRecord;
      console.log('✅ 详情加载成功');
      console.log('📹 媒体文件信息:', {
        detection_type: detailRecord.detection_type,
        original_file: detailRecord.original_file,
        result_file: detailRecord.result_file,
        original_filename: detailRecord.original_filename,
        result_filename: detailRecord.result_filename,
      });
    } else {
      console.error('❌ 获取详情失败 - 数据为空:', response);
      message.error('获取详情失败 - 数据为空');
    }
  } catch (error) {
    console.error('❌ 获取详情异常:', error);
    message.error('获取详情失败，请检查网络连接');
  } finally {
    detailLoading.value = false;
  }
};

const deleteRecord = async (id: string) => {
  console.log('🗑️ 点击删除按钮');
  console.log('🗑️ 删除记录ID:', id);

  if (!userStore.userInfo?.user_id) {
    message.error('用户信息不存在，请重新登录');
    return;
  }

  try {
    console.log('🗑️ 删除检测记录:', id);

    const response = await detectionHistoryApi.deleteDetectionRecord(
      userStore.userInfo.user_id,
      id
    );

    if (response && (response.success === true || response.success === undefined)) {
      message.success('记录删除成功');
      // 从选择列表中移除已删除的记录
      selectedRecordIds.value = selectedRecordIds.value.filter((selectedId) => selectedId !== id);
      // 重新加载数据
      await loadDetectionHistory();
    } else {
      console.error('❌ 删除记录失败:', response?.message);
      message.error(response?.message || '删除记录失败');
    }
  } catch (error) {
    console.error('❌ 删除记录异常:', error);
    message.error('删除记录失败，请检查网络连接');
  }
};

// 全选/取消全选
const isAllSelected = computed(() => {
  return (
    detectionHistory.value.length > 0 &&
    selectedRecordIds.value.length === detectionHistory.value.length
  );
});

const isIndeterminate = computed(() => {
  return (
    selectedRecordIds.value.length > 0 &&
    selectedRecordIds.value.length < detectionHistory.value.length
  );
});

const handleSelectAll = (e: any) => {
  if (e.target.checked) {
    // 全选
    selectedRecordIds.value = detectionHistory.value.map((record) => record.id);
  } else {
    // 取消全选
    selectedRecordIds.value = [];
  }
};

// 单个记录选择
const handleRecordSelect = (recordId: string, checked: boolean) => {
  if (checked) {
    if (!selectedRecordIds.value.includes(recordId)) {
      selectedRecordIds.value.push(recordId);
    }
  } else {
    selectedRecordIds.value = selectedRecordIds.value.filter((id) => id !== recordId);
  }
};

// 批量删除
const batchDeleteRecords = async () => {
  if (selectedRecordIds.value.length === 0) {
    message.warning('请先选择要删除的记录');
    return;
  }

  if (!userStore.userInfo?.user_id) {
    message.error('用户信息不存在，请重新登录');
    return;
  }

  Modal.confirm({
    title: '确认批量删除',
    content: `确定要删除选中的 ${selectedRecordIds.value.length} 条记录吗？此操作不可恢复。`,
    okText: '确定删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      batchDeleting.value = true;
      try {
        console.log('🗑️ 批量删除记录:', selectedRecordIds.value);

        const response = await detectionHistoryApi.batchDeleteDetectionRecords(
          userStore.userInfo.user_id,
          selectedRecordIds.value
        );

        console.log('🗑️ 批量删除响应:', response);

        if (response && (response.success === true || response.success === undefined)) {
          message.success(`成功删除 ${selectedRecordIds.value.length} 条记录`);
          selectedRecordIds.value = [];
          // 重新加载数据
          await loadDetectionHistory();
        } else {
          const errorMsg = response?.message || '批量删除失败';
          console.error('❌ 批量删除失败:', errorMsg);
          message.error(errorMsg);
        }
      } catch (error: any) {
        console.error('❌ 批量删除异常:', error);
        console.error('❌ 错误详情:', {
          message: error?.message,
          response: error?.response,
          status: error?.response?.status,
          data: error?.response?.data,
        });

        let errorMessage = '批量删除失败，请检查网络连接';

        if (error?.response) {
          const status = error.response.status;
          const data = error.response.data;

          if (status === 404) {
            errorMessage = '部分记录不存在或已被删除';
          } else if (status === 403) {
            errorMessage = '没有权限删除这些记录';
          } else if (status === 500) {
            errorMessage = '服务器错误，请稍后重试';
          } else if (data?.message) {
            errorMessage = data.message;
          } else if (data?.detail) {
            errorMessage = data.detail;
          } else {
            errorMessage = `批量删除失败 (${status})`;
          }
        } else if (error?.message) {
          errorMessage = error.message;
        }

        message.error(errorMessage);
      } finally {
        batchDeleting.value = false;
      }
    },
  });
};

const exportHistory = async () => {
  if (!userStore.userInfo?.user_id) {
    message.error('用户信息不存在，请重新登录');
    return;
  }

  try {
    console.log('📤 导出检测历史');

    const params = {
      search: searchKeyword.value || undefined,
      class_filter: filterClass.value || undefined,
      start_date: dateRange.value?.[0]?.format('YYYY-MM-DD'),
      end_date: dateRange.value?.[1]?.format('YYYY-MM-DD'),
    };

    const blob = await detectionHistoryApi.exportDetectionHistory(
      userStore.userInfo.user_id,
      params
    );

    // 创建下载链接
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `检测历史_${new Date().toISOString().split('T')[0]}.xlsx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    message.success('检测历史导出成功');
  } catch (error) {
    console.error('❌ 导出历史异常:', error);
    message.error('导出检测历史失败，请检查网络连接');
  }
};

const formatDate = (date: Date) => {
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const getDetectionColor = (className: string) => {
  const colorMap: Record<string, string> = {
    person: 'blue',
    car: 'green',
    dog: 'orange',
    cat: 'purple',
    bicycle: 'cyan',
    motorcycle: 'red',
  };
  return colorMap[className] || 'default';
};

const getTagColor = (className: string) => {
  const colorMap: Record<string, string> = {
    person: 'blue',
    car: 'green',
    dog: 'orange',
    cat: 'purple',
    bicycle: 'cyan',
    motorcycle: 'red',
    pothole: 'red',
    'open-manholes': 'volcano',
    default: 'default',
  };
  return colorMap[className] || 'default';
};

// 测试点击事件
const closeDetailModal = () => {
  detailModalVisible.value = false;
  selectedRecord.value = null;
  detailLoading.value = false;
};

const handleVideoError = (event: Event) => {
  console.error('❌ 视频加载失败:', event);
  const target = event.target as HTMLVideoElement;
  console.error('❌ 视频URL:', target.src);
  message.error('视频加载失败，请检查文件路径或网络连接');
};

const handleVideoLoadStart = (event: Event) => {
  console.log('📹 视频开始加载:', event);
  const target = event.target as HTMLVideoElement;
  console.log('📹 视频URL:', target.src);
};

const downloadVideo = (url: string, filename: string) => {
  console.log('📥 下载视频:', url, filename);
  try {
    const link = document.createElement('a');
    link.href = getFullFileUrl(url);
    link.download = filename || 'video.mp4';
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    message.success('视频下载已开始');
  } catch (error) {
    console.error('❌ 下载视频失败:', error);
    message.error('下载视频失败');
  }
};

const handleImageError = (event: Event) => {
  console.error('❌ 图片加载失败:', event);
  const target = event.target as HTMLImageElement;
  console.error('❌ 图片URL:', target.src);
  message.error('图片加载失败，请检查文件路径或网络连接');
};

const handleImageLoad = (event: Event) => {
  console.log('🖼️ 图片加载成功:', event);
  const target = event.target as HTMLImageElement;
  console.log('🖼️ 图片URL:', target.src);
};

const downloadImage = (url: string, filename: string) => {
  console.log('📥 下载图片:', url, filename);
  try {
    const link = document.createElement('a');
    link.href = getFullFileUrl(url);
    link.download = filename || 'image.jpg';
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    message.success('图片下载已开始');
  } catch (error) {
    console.error('❌ 下载图片失败:', error);
    message.error('下载图片失败');
  }
};

const openImageInNewTab = (url: string) => {
  console.log('🖼️ 在新窗口打开图片:', url);
  try {
    window.open(getFullFileUrl(url), '_blank');
  } catch (error) {
    console.error('❌ 打开图片失败:', error);
    message.error('打开图片失败');
  }
};

const openVideoInNewTab = (url: string) => {
  console.log('🎥 在新窗口打开视频:', url);
  try {
    window.open(getFullFileUrl(url), '_blank');
  } catch (error) {
    console.error('❌ 打开视频失败:', error);
    message.error('打开视频失败');
  }
};

// 处理图片预览的z-index
const handleImagePreview = () => {
  // 延迟执行，确保预览组件已经渲染
  setTimeout(() => {
    const previewElements = document.querySelectorAll(
      '.ant-image-preview, .ant-image-preview-wrap, .ant-image-preview-mask, .ant-image-preview-body, .ant-image-preview-img, .ant-image-preview-operations'
    );
    previewElements.forEach((element: any) => {
      if (element) {
        element.style.zIndex = '10002';
      }
    });
  }, 100);
};

const showImagePlaceholder = (event: Event) => {
  const target = event.target as HTMLImageElement;
  target.style.display = 'none';
  const placeholder = document.createElement('div');
  placeholder.innerHTML = `
    <div style="text-align: center; color: #999; padding: 20px;">
      <div style="font-size: 48px; margin-bottom: 10px;">🖼️</div>
      <div>图片加载失败</div>
      <div style="font-size: 12px; margin-top: 5px;">请尝试下载或在新窗口查看</div>
    </div>
  `;
  target.parentNode?.appendChild(placeholder);
};

// 组件挂载
onMounted(() => {
  console.log('🚀 检测历史页面挂载');
  console.log('👤 用户信息:', userStore.userInfo);
  console.log('🆔 用户ID:', userStore.userInfo?.user_id);
  loadLayout();
  window.addEventListener('detectionHistoryLayoutChanged', handleLayoutChange);
  loadDetectionHistory();
});

onUnmounted(() => {
  window.removeEventListener('detectionHistoryLayoutChanged', handleLayoutChange);
});
</script>

<style scoped lang="scss">
.detection-history-page {
  padding: 24px;
  background: var(--theme-page-bg, #f5f5f5);
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;

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

  .filter-section {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 24px;
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
    overflow-x: hidden;
  }

  .history-content {
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
    overflow-x: hidden;

    .no-data {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 400px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      color: var(--theme-text-secondary, #9ca3af);

      .no-data-icon {
        font-size: 4rem;
        margin-bottom: 16px;
      }

      p {
        margin: 4px 0;
        font-size: 1.1rem;
      }

      .no-data-hint {
        font-size: 0.9rem;
        color: var(--theme-text-secondary, #d1d5db);
      }
    }

    // 网格布局 - 完全独立
    .history-grid {
      display: grid !important;
      grid-template-columns: 1fr 1fr !important;
      gap: 16px;
      width: 100%;
      max-width: 100%;
      box-sizing: border-box;

      @media (max-width: 768px) {
        grid-template-columns: 1fr !important;
      }

      .history-item {
        margin-bottom: 0;
        cursor: pointer;
        transition: all 0.3s ease;
        min-width: 0;
        max-width: 100%;
        box-sizing: border-box;

        &:hover {
          transform: translateY(-2px);
        }

        .item-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
          overflow: hidden;
          transition: all 0.3s ease;
          border: 1px solid #f0f0f0;
          height: 100%;
          width: 100%;
          max-width: 100%;
          box-sizing: border-box;
          position: relative;

          &:hover {
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
            border-color: var(--theme-card-border, #e6f7ff);
          }

          .item-checkbox {
            position: absolute;
            top: 12px;
            left: 12px;
            z-index: 10;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 4px;
            padding: 4px;
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          }
        }

        .media-section {
          position: relative;
          height: 400px;
          background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
          overflow: hidden;
          width: 100%;
          max-width: 100%;
          box-sizing: border-box;

          .media-container {
            width: 100%;
            height: 100%;
            position: relative;
            max-width: 100%;
            box-sizing: border-box;

            .media-thumbnail {
              width: 100%;
              height: 100%;
              position: relative;
              overflow: hidden;
              max-width: 100%;
              box-sizing: border-box;

              img,
              video {
                width: 100%;
                height: 100%;
                max-width: 100%;
                object-fit: cover;
                transition: transform 0.3s ease;
                display: block;
                position: absolute;
                top: 0;
                left: 0;
                box-sizing: border-box;
              }

              video {
                pointer-events: none;
              }

              &:hover img,
              &:hover video {
                transform: scale(1.05);
              }

              .media-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(
                  to bottom,
                  rgba(0, 0, 0, 0.1) 0%,
                  rgba(0, 0, 0, 0.3) 50%,
                  rgba(0, 0, 0, 0.6) 100%
                );
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                padding: 12px;
                opacity: 0;
                transition: opacity 0.3s ease;
                z-index: 2;
                pointer-events: none;

                .play-icon {
                  align-self: center;
                  font-size: 2rem;
                  color: white;
                  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
                }

                .overlay-stats {
                  display: flex;
                  gap: 8px;
                  align-self: flex-end;

                  .stat-item {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    background: rgba(255, 255, 255, 0.9);
                    padding: 4px 8px;
                    border-radius: 6px;
                    backdrop-filter: blur(10px);

                    .stat-number {
                      font-weight: 600;
                      font-size: 0.9rem;
                      color: var(--theme-primary, #1890ff);
                    }

                    .stat-label {
                      font-size: 0.7rem;
                      color: #666;
                    }
                  }
                }
              }

              &:hover .media-overlay {
                opacity: 1;
              }

              .media-type-badge {
                position: absolute;
                top: 8px;
                right: 8px;
                padding: 4px 8px;
                border-radius: 16px;
                font-size: 0.7rem;
                font-weight: 500;
                backdrop-filter: blur(10px);
                z-index: 3;
                pointer-events: none;

                &.video-badge {
                  background: rgba(24, 144, 255, 0.9);
                  color: white;
                }

                &.image-badge {
                  background: rgba(82, 196, 26, 0.9);
                  color: white;
                }
              }
            }
          }
        }

        .info-section {
          padding: 16px;
          width: 100%;
          max-width: 100%;
          box-sizing: border-box;

          .item-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
            gap: 12px;

            .file-info {
              flex: 1;
              min-width: 0;
              max-width: 100%;
              box-sizing: border-box;

              .item-title {
                font-size: 1.1rem;
                font-weight: 600;
                color: var(--theme-text-primary, #1f2937);
                margin: 0 0 8px 0;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                max-width: 100%;
                box-sizing: border-box;
              }

              .item-meta {
                display: flex;
                flex-wrap: wrap;
                gap: 12px;

                .meta-item {
                  display: flex;
                  align-items: center;
                  gap: 4px;
                  font-size: 0.8rem;
                  color: var(--theme-text-secondary, #6b7280);

                  .anticon {
                    color: var(--theme-text-secondary, #9ca3af);
                    font-size: 0.75rem;
                  }
                }
              }
            }

            .item-actions {
              display: flex;
              gap: 8px;
              flex-shrink: 0;
              min-width: 0;
              box-sizing: border-box;

              .action-btn {
                border-radius: 8px;
                font-weight: 500;
                transition: all 0.2s ease;
                white-space: nowrap;
                flex-shrink: 0;

                &:hover {
                  transform: translateY(-1px);
                  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                }
              }
            }
          }

          .detection-results {
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;

            .results-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 10px;
              width: 100%;
              max-width: 100%;
              box-sizing: border-box;
              gap: 8px;

              .results-title {
                font-weight: 600;
                color: var(--theme-text-primary, #374151);
                font-size: 0.9rem;
                flex-shrink: 0;
                min-width: 0;
              }

              .results-count {
                font-size: 0.8rem;
                color: #6b7280;
                background: var(--theme-content-bg, #f3f4f6);
                padding: 3px 8px;
                border-radius: 12px;
                flex-shrink: 0;
                white-space: nowrap;
              }
            }

            .result-tags {
              display: flex;
              flex-wrap: wrap;
              gap: 8px;
              width: 100%;
              max-width: 100%;
              box-sizing: border-box;

              .result-tag {
                border-radius: 14px;
                font-size: 0.75rem;
                font-weight: 500;
                padding: 3px 10px;
                border: none;
                transition: all 0.2s ease;

                &:hover {
                  transform: translateY(-1px);
                  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }
              }

              .more-tag {
                background: var(--theme-content-bg, #f3f4f6);
                color: #6b7280;
                border: 1px solid #e5e7eb;
              }
            }
          }
        }
      }
    }

    // 列表布局 - 完全独立
    .history-list-layout {
      display: grid !important;
      grid-template-columns: 1fr !important;
      gap: 16px;

      .history-item-list {
        margin-bottom: 0;
        cursor: pointer;
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-2px);
        }

        .item-card-list {
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
          border: 1px solid #f0f0f0;
          display: flex;
          align-items: center;
          padding: 0;
          overflow: hidden;
          transition: all 0.3s ease;
          position: relative;

          &:hover {
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
            border-color: var(--theme-card-border, #e6f7ff);
          }

          .item-checkbox-list {
            position: absolute;
            top: 12px;
            left: 12px;
            z-index: 10;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 4px;
            padding: 4px;
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          }

          .media-section-list {
            flex-shrink: 0;
            width: 200px;
            height: 150px;
            position: relative;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            overflow: hidden;

            .media-container-list {
              width: 100%;
              height: 100%;
              position: relative;

              .media-thumbnail-list {
                width: 100%;
                height: 100%;
                position: relative;
                overflow: hidden;

                img,
                video {
                  width: 100%;
                  height: 100%;
                  object-fit: cover;
                  transition: transform 0.3s ease;
                  display: block;
                  position: absolute;
                  top: 0;
                  left: 0;
                }

                video {
                  pointer-events: none;
                }

                &:hover img,
                &:hover video {
                  transform: scale(1.05);
                }

                .media-overlay-list {
                  position: absolute;
                  top: 0;
                  left: 0;
                  right: 0;
                  bottom: 0;
                  background: linear-gradient(
                    to bottom,
                    rgba(0, 0, 0, 0.1) 0%,
                    rgba(0, 0, 0, 0.3) 50%,
                    rgba(0, 0, 0, 0.6) 100%
                  );
                  display: flex;
                  flex-direction: column;
                  justify-content: space-between;
                  padding: 8px;
                  opacity: 0;
                  transition: opacity 0.3s ease;
                  z-index: 2;
                  pointer-events: none;

                  .play-icon {
                    align-self: center;
                    font-size: 2rem;
                    color: white;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
                  }

                  .overlay-stats-list {
                    display: flex;
                    gap: 8px;
                    align-self: flex-end;

                    .stat-item {
                      display: flex;
                      flex-direction: column;
                      align-items: center;
                      background: rgba(255, 255, 255, 0.9);
                      padding: 4px 8px;
                      border-radius: 6px;
                      backdrop-filter: blur(10px);

                      .stat-number {
                        font-weight: 600;
                        font-size: 0.9rem;
                        color: var(--theme-primary, #1890ff);
                      }

                      .stat-label {
                        font-size: 0.7rem;
                        color: #666;
                      }
                    }
                  }
                }

                &:hover .media-overlay-list {
                  opacity: 1;
                }

                .media-type-badge {
                  position: absolute;
                  top: 8px;
                  right: 8px;
                  padding: 4px 8px;
                  border-radius: 16px;
                  font-size: 0.7rem;
                  font-weight: 500;
                  backdrop-filter: blur(10px);
                  z-index: 3;
                  pointer-events: none;

                  &.video-badge {
                    background: rgba(24, 144, 255, 0.9);
                    color: white;
                  }

                  &.image-badge {
                    background: rgba(82, 196, 26, 0.9);
                    color: white;
                  }
                }
              }
            }
          }

          .info-section-list {
            flex: 1;
            min-width: 0;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;

            .item-header-list {
              display: flex;
              justify-content: space-between;
              align-items: flex-start;

              .file-info-list {
                flex: 1;

                .item-title-list {
                  font-size: 1rem;
                  font-weight: 600;
                  color: var(--theme-text-primary, #1f2937);
                  margin: 0 0 8px 0;
                  line-height: 1.4;
                  display: -webkit-box;
                  -webkit-line-clamp: 2;
                  -webkit-box-orient: vertical;
                  overflow: hidden;
                }

                .item-meta-list {
                  display: flex;
                  flex-wrap: wrap;
                  gap: 12px;

                  .meta-item {
                    display: flex;
                    align-items: center;
                    gap: 4px;
                    font-size: 0.8rem;
                    color: var(--theme-text-secondary, #6b7280);

                    .anticon {
                      color: var(--theme-text-secondary, #9ca3af);
                      font-size: 0.75rem;
                    }
                  }
                }
              }

              .item-actions-list {
                display: flex;
                gap: 8px;
                flex-shrink: 0;

                .action-btn {
                  border-radius: 8px;
                  font-weight: 500;
                  transition: all 0.2s ease;

                  &:hover {
                    transform: translateY(-1px);
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                  }
                }
              }
            }

            .detection-results-list {
              .results-header-list {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;

                .results-title {
                  font-weight: 600;
                  color: var(--theme-text-primary, #374151);
                  font-size: 0.9rem;
                }

                .results-count {
                  font-size: 0.8rem;
                  color: var(--theme-text-secondary, #6b7280);
                  background: var(--theme-content-bg, #f3f4f6);
                  padding: 3px 8px;
                  border-radius: 12px;
                }
              }

              .result-tags {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;

                .result-tag {
                  border-radius: 14px;
                  font-size: 0.75rem;
                  font-weight: 500;
                  padding: 3px 10px;
                  border: none;
                  transition: all 0.2s ease;

                  &:hover {
                    transform: translateY(-1px);
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                  }
                }

                .more-tag {
                  background: var(--theme-content-bg, #f3f4f6);
                  color: var(--theme-text-secondary, #6b7280);
                  border: 1px solid #e5e7eb;
                }
              }
            }
          }
        }
      }
    }

    // 流式布局 - 完全独立（瀑布流效果）
    .history-flow {
      column-count: 3 !important;
      column-gap: 20px !important;
      column-fill: balance;

      @media (max-width: 1200px) {
        column-count: 2 !important;
      }

      @media (max-width: 768px) {
        column-count: 1 !important;
      }

      .history-item-flow {
        break-inside: avoid;
        margin-bottom: 20px;
        page-break-inside: avoid;

        .item-card-flow {
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
          border: 1px solid #f0f0f0;
          overflow: hidden;
          transition: all 0.3s ease;
          height: 100%;
          display: flex;
          flex-direction: column;
          position: relative;

          &:hover {
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
            border-color: var(--theme-card-border, #e6f7ff);
            transform: translateY(-4px);
          }

          .item-checkbox-flow {
            position: absolute;
            top: 12px;
            left: 12px;
            z-index: 10;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 4px;
            padding: 4px;
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          }

          .media-section-flow {
            position: relative;
            height: 200px;
            flex-shrink: 0;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            overflow: hidden;

            .media-container-flow {
              width: 100%;
              height: 100%;
              position: relative;

              .media-thumbnail-flow {
                width: 100%;
                height: 100%;
                position: relative;
                overflow: hidden;

                img,
                video {
                  width: 100%;
                  height: 100%;
                  object-fit: cover;
                  transition: transform 0.3s ease;
                  display: block;
                  position: absolute;
                  top: 0;
                  left: 0;
                }

                video {
                  pointer-events: none;
                }

                &:hover img,
                &:hover video {
                  transform: scale(1.1);
                }

                .media-overlay-flow {
                  position: absolute;
                  top: 0;
                  left: 0;
                  right: 0;
                  bottom: 0;
                  background: linear-gradient(
                    to bottom,
                    rgba(0, 0, 0, 0.1) 0%,
                    rgba(0, 0, 0, 0.4) 100%
                  );
                  display: flex;
                  flex-direction: column;
                  justify-content: space-between;
                  padding: 12px;
                  opacity: 0;
                  transition: opacity 0.3s ease;
                  z-index: 2;
                  pointer-events: none;

                  .play-icon {
                    align-self: center;
                    font-size: 2rem;
                    color: white;
                  }

                  .overlay-stats-flow {
                    display: flex;
                    gap: 8px;
                    align-self: flex-end;

                    .stat-item {
                      display: flex;
                      flex-direction: column;
                      align-items: center;
                      background: rgba(255, 255, 255, 0.9);
                      padding: 4px 8px;
                      border-radius: 6px;

                      .stat-number {
                        font-weight: 600;
                        font-size: 0.9rem;
                        color: var(--theme-primary, #1890ff);
                      }

                      .stat-label {
                        font-size: 0.7rem;
                        color: #666;
                      }
                    }
                  }
                }

                &:hover .media-overlay-flow {
                  opacity: 1;
                }

                .media-type-badge {
                  position: absolute;
                  top: 8px;
                  right: 8px;
                  padding: 4px 8px;
                  border-radius: 16px;
                  font-size: 0.7rem;
                  backdrop-filter: blur(10px);
                  z-index: 3;
                  pointer-events: none;

                  &.video-badge {
                    background: rgba(24, 144, 255, 0.9);
                    color: white;
                  }

                  &.image-badge {
                    background: rgba(82, 196, 26, 0.9);
                    color: white;
                  }
                }
              }
            }
          }

          .info-section-flow {
            padding: 16px;
            flex: 1;
            display: flex;
            flex-direction: column;

            .item-title-flow {
              font-size: 1rem;
              font-weight: 600;
              color: #1f2937;
              margin: 0 0 8px 0;
              overflow: hidden;
              text-overflow: ellipsis;
              display: -webkit-box;
              -webkit-line-clamp: 2;
              -webkit-box-orient: vertical;
              line-height: 1.4;
            }

            .item-meta-flow {
              display: flex;
              gap: 12px;
              margin-bottom: 12px;
              flex-wrap: wrap;

              .meta-item {
                display: flex;
                align-items: center;
                gap: 4px;
                font-size: 0.8rem;
                color: #6b7280;
              }
            }

            .detection-results-flow {
              margin-top: auto;

              .result-tags {
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
              }
            }
          }
        }
      }
    }

    .pagination-wrapper {
      display: flex;
      justify-content: center;
      margin-top: 24px;
      padding: 20px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
  }
}

.detail-content {
  .detail-layout {
    display: flex;
    gap: 24px;
    min-height: 400px;

    .detail-left {
      flex: 0 0 50%;
      min-width: 0;

      .detail-media {
        .media-comparison {
          display: flex;
          flex-direction: row;
          gap: 16px;

          .media-item {
            flex: 1;
            text-align: center;

            h5 {
              margin-bottom: 10px;
              color: #1890ff;
              font-weight: 500;
              font-size: 14px;
            }

            img,
            video {
              max-width: 100%;
              max-height: 150px;
              width: 100%;
              height: auto;
              border-radius: 8px;
              box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
              border: 2px solid #f0f0f0;
              transition: border-color 0.3s;
              object-fit: contain;
              overflow: hidden;

              &:hover {
                border-color: #1890ff;
              }
            }

            video {
              background: #000;
            }
          }
        }
      }
    }

    .detail-right {
      flex: 0 0 50%;
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: 20px;

      .detail-info {
        h4 {
          color: var(--theme-text-primary, #1e293b);
          margin-bottom: 16px;
          font-size: 18px;
          font-weight: 600;
        }

        .info-grid {
          display: flex;
          flex-direction: column;
          gap: 12px;

          .info-item {
            display: flex;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;

            &:last-child {
              border-bottom: none;
            }

            .info-label {
              font-weight: 500;
              color: var(--theme-text-secondary, #64748b);
              min-width: 100px;
              flex-shrink: 0;
            }

            .info-value {
              color: var(--theme-text-primary, #1e293b);
              font-weight: 400;
            }
          }
        }
      }

      .detail-detections {
        flex: 1;

        h5 {
          color: var(--theme-text-primary, #1e293b);
          margin-bottom: 12px;
          font-size: 16px;
          font-weight: 500;
        }

        .detection-table {
          :deep(.ant-table) {
            border-radius: 8px;
            overflow: hidden;
          }
        }
      }
    }
  }
}

// 图片预览层级修复
:deep(.ant-image-preview) {
  z-index: 10002 !important;
}

:deep(.ant-image-preview-wrap) {
  z-index: 10002 !important;
}

:deep(.ant-image-preview-mask) {
  z-index: 10002 !important;
}

:deep(.ant-image-preview-body) {
  z-index: 10002 !important;
}

:deep(.ant-image-preview-img) {
  z-index: 10002 !important;
}

:deep(.ant-image-preview-operations) {
  z-index: 10002 !important;
}

:deep(.ant-image-preview-switch-left) {
  z-index: 10002 !important;
}

:deep(.ant-image-preview-switch-right) {
  z-index: 10002 !important;
}

// 全局图片预览层级修复
.ant-image-preview {
  z-index: 10002 !important;
}

.ant-image-preview-wrap {
  z-index: 10002 !important;
}

.ant-image-preview-mask {
  z-index: 10002 !important;
}

.ant-image-preview-body {
  z-index: 10002 !important;
}

.ant-image-preview-img {
  z-index: 10002 !important;
}

.ant-image-preview-operations {
  z-index: 10002 !important;
}

// 强制设置所有图片预览相关元素的z-index
.ant-image-preview * {
  z-index: 10002 !important;
}

// 响应式设计
@media (max-width: 1200px) {
  .detail-content {
    .detail-layout {
      flex-direction: column;
      gap: 20px;

      .detail-left {
        flex: 1;
      }

      .detail-right {
        flex: 1;
      }
    }
  }
}

@media (max-width: 768px) {
  .detection-history-page {
    padding: 16px;

    .filter-section {
      :deep(.ant-col) {
        margin-bottom: 12px;
      }
    }

    .history-content {
      .history-grid {
        grid-template-columns: 1fr !important;
        gap: 12px;

        .history-item {
          .item-header {
            flex-direction: column;
            gap: 8px;

            .item-actions {
              width: 100%;
              justify-content: flex-end;
            }
          }

          .media-section {
            height: 120px;
          }
        }
      }

      .history-list-layout {
        grid-template-columns: 1fr !important;
        gap: 12px;

        .history-item-list {
          .item-card-list {
            flex-direction: column;

            .media-section-list {
              width: 100%;
              height: 200px;
            }
          }
        }
      }

      .history-flow {
        grid-template-columns: 1fr !important;
        gap: 12px;
      }
    }
  }
}

@media (max-width: 768px) {
  .detail-content {
    .detail-layout {
      .detail-right {
        .detail-info {
          .info-grid {
            .info-item {
              flex-direction: column;
              align-items: flex-start;
              gap: 4px;

              .info-label {
                min-width: auto;
              }
            }
          }
        }
      }
    }
  }
}
</style>
