<template>
  <div class="experiment-detail" v-loading="loading">
    <template v-if="experiment">
      <div class="detail-header">
        <el-button text @click="router.push('/experiments')">
          <el-icon><ArrowLeft /></el-icon> 返回列表
        </el-button>
        <div class="header-actions">
          <el-tag :type="getStatusType(experiment.status)" size="large">{{ getStatusLabel(experiment.status) }}</el-tag>
          <el-button v-if="experiment.status === 'planning'" type="success" @click="handleStart">开始实验</el-button>
          <el-button v-if="experiment.status === 'running'" type="primary" @click="handleComplete">完成实验</el-button>
          <el-button type="danger" @click="handleDelete">删除</el-button>
        </div>
      </div>

      <el-row :gutter="20">
        <el-col :span="16">
          <!-- 基本信息 -->
          <el-card class="detail-card">
            <h2>{{ experiment.title }}</h2>
            <p class="desc">{{ experiment.description || '暂无描述' }}</p>
            <el-divider />
            <el-descriptions :column="2" border>
              <el-descriptions-item label="模型架构">{{ experiment.model_architecture || '-' }}</el-descriptions-item>
              <el-descriptions-item label="框架">{{ experiment.framework || '-' }}</el-descriptions-item>
              <el-descriptions-item label="模型版本">{{ experiment.model_version || '-' }}</el-descriptions-item>
              <el-descriptions-item label="进度">
                <el-progress :percentage="experiment.progress" :stroke-width="10" />
              </el-descriptions-item>
              <el-descriptions-item label="开始时间">{{ formatDate(experiment.start_date) }}</el-descriptions-item>
              <el-descriptions-item label="结束时间">{{ formatDate(experiment.end_date) }}</el-descriptions-item>
              <el-descriptions-item label="耗时" :span="2">
                {{ experiment.duration ? formatDuration(experiment.duration) : '-' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <!-- 超参数 -->
          <el-card v-if="experiment.hyperparameters" class="detail-card">
            <template #header><span>⚙️ 超参数配置</span></template>
            <pre class="json-block">{{ JSON.stringify(experiment.hyperparameters, null, 2) }}</pre>
          </el-card>

          <!-- 数据集信息 -->
          <el-card v-if="experiment.dataset_info" class="detail-card">
            <template #header><span>📊 数据集信息</span></template>
            <pre class="json-block">{{ JSON.stringify(experiment.dataset_info, null, 2) }}</pre>
          </el-card>

          <!-- 实验结果 -->
          <el-card v-if="experiment.results" class="detail-card">
            <template #header><span>📈 实验结果</span></template>
            <pre class="json-block">{{ JSON.stringify(experiment.results, null, 2) }}</pre>
          </el-card>

          <!-- 备注 -->
          <el-card v-if="experiment.notes" class="detail-card">
            <template #header><span>📝 备注</span></template>
            <p>{{ experiment.notes }}</p>
          </el-card>
        </el-col>

        <el-col :span="8">
          <!-- 音频文件 -->
          <el-card class="detail-card">
            <template #header>
              <div class="card-header">
                <span>🎵 音频文件 ({{ audioFiles.length }})</span>
                <el-upload
                  :action="`/api/experiments/${experiment.id}/audio`"
                  :headers="uploadHeaders"
                  :on-success="handleUploadSuccess"
                  :show-file-list="false"
                  accept=".wav,.mp3,.flac,.ogg,.m4a"
                >
                  <el-button size="small" type="primary">上传</el-button>
                </el-upload>
              </div>
            </template>
            <div class="audio-list">
              <div v-for="audio in audioFiles" :key="audio.id" class="audio-item">
                <div class="audio-info">
                  <el-icon><Headset /></el-icon>
                  <div>
                    <div class="audio-name">{{ audio.file_name }}</div>
                    <div class="audio-meta">{{ audio.duration_formatted }} · {{ audio.file_size_mb }}MB</div>
                  </div>
                </div>
                <el-button text type="danger" size="small" @click="deleteAudio(audio.id)">删除</el-button>
              </div>
              <el-empty v-if="audioFiles.length === 0" description="暂无音频文件" :image-size="60" />
            </div>
          </el-card>

          <!-- 实验指标 -->
          <el-card class="detail-card">
            <template #header><span>📊 实验指标摘要</span></template>
            <div v-if="Object.keys(metricsSummary).length" class="metrics-list">
              <div v-for="(data, name) in metricsSummary" :key="name" class="metric-item">
                <div class="metric-name">{{ name }}</div>
                <div class="metric-values">
                  <span>最新: {{ data.latest?.metric_value?.toFixed(4) }}</span>
                  <span>最佳: {{ data.best?.metric_value?.toFixed(4) }}</span>
                  <span>平均: {{ data.average?.toFixed(4) }}</span>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无指标数据" :image-size="60" />
          </el-card>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { experimentApi, audioApi, metricApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()

const experiment = ref<any>(null)
const audioFiles = ref<any[]>([])
const metricsSummary = ref<any>({})
const loading = ref(false)

const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
}))

function getStatusType(status: string) {
  const types: Record<string, string> = { planning: 'info', running: 'warning', completed: 'success', failed: 'danger' }
  return types[status] || 'info'
}

function getStatusLabel(status: string) {
  const labels: Record<string, string> = { planning: '规划中', running: '进行中', completed: '已完成', failed: '已失败' }
  return labels[status] || status
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function formatDuration(seconds: number) {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}小时${m}分钟${s}秒`
  if (m > 0) return `${m}分钟${s}秒`
  return `${s}秒`
}

async function loadExperiment() {
  loading.value = true
  try {
    const id = Number(route.params.id)
    experiment.value = await experimentApi.getOne(id)
    audioFiles.value = await audioApi.getList(id) as any
    metricsSummary.value = await metricApi.getSummary(id) as any
  } catch (e) {
    ElMessage.error('加载实验失败')
  } finally {
    loading.value = false
  }
}

async function handleStart() {
  try {
    await experimentApi.start(experiment.value.id)
    ElMessage.success('实验已开始')
    loadExperiment()
  } catch (e) {}
}

async function handleComplete() {
  try {
    await experimentApi.complete(experiment.value.id)
    ElMessage.success('实验已完成')
    loadExperiment()
  } catch (e) {}
}

async function handleDelete() {
  await ElMessageBox.confirm('确定要删除这个实验吗？', '确认删除', { type: 'warning' })
  try {
    await experimentApi.delete(experiment.value.id)
    ElMessage.success('删除成功')
    router.push('/experiments')
  } catch (e) {}
}

function handleUploadSuccess() {
  ElMessage.success('上传成功')
  loadExperiment()
}

async function deleteAudio(audioId: number) {
  await ElMessageBox.confirm('确定要删除这个音频文件吗？', '确认删除', { type: 'warning' })
  try {
    await audioApi.delete(audioId)
    ElMessage.success('删除成功')
    loadExperiment()
  } catch (e) {}
}

onMounted(loadExperiment)
</script>

<style scoped>
.experiment-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.detail-card {
  margin-bottom: 20px;
}

.detail-card h2 {
  font-size: 22px;
  margin-bottom: 8px;
}

.desc {
  color: #666;
  margin-bottom: 16px;
}

.json-block {
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  font-size: 13px;
  overflow-x: auto;
  font-family: 'Consolas', monospace;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.audio-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.audio-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  border-radius: 6px;
  background: #f9f9f9;
}

.audio-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.audio-name {
  font-size: 13px;
  font-weight: 500;
}

.audio-meta {
  font-size: 11px;
  color: #999;
}

.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-item {
  padding: 8px;
  background: #f9f9f9;
  border-radius: 6px;
}

.metric-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.metric-values {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #666;
}
</style>