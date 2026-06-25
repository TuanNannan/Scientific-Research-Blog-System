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

          <!-- 实验阶段 -->
          <el-card class="detail-card">
            <template #header>
              <div class="card-header">
                <span>📋 实验阶段</span>
                <el-button v-if="stages.length === 0" size="small" type="primary" @click="handleInitStages">
                  初始化阶段
                </el-button>
              </div>
            </template>
            <div v-if="stages.length > 0" class="stages-container">
              <div v-for="(stage, index) in stages" :key="stage.id" class="stage-item">
                <div class="stage-connector" v-if="index < stages.length - 1">
                  <div class="connector-line" :class="{ active: stage.status === 'completed' }"></div>
                </div>
                <div class="stage-node" :class="stage.status">
                  <div class="stage-icon">
                    <el-icon v-if="stage.status === 'completed'"><Select /></el-icon>
                    <el-icon v-else-if="stage.status === 'in_progress'"><Loading /></el-icon>
                    <el-icon v-else-if="stage.status === 'skipped'"><Close /></el-icon>
                    <span v-else>{{ index + 1 }}</span>
                  </div>
                  <div class="stage-info">
                    <div class="stage-name">{{ stage.stage_label }}</div>
                    <div class="stage-status">{{ getStatusLabel(stage.status) }}</div>
                    <el-progress v-if="stage.status === 'in_progress'" :percentage="stage.progress" :stroke-width="4" />
                  </div>
                  <div class="stage-actions">
                    <el-button v-if="stage.status === 'pending'" size="small" @click="handleStartStage(stage)">开始</el-button>
                    <el-button v-if="stage.status === 'in_progress'" size="small" type="success" @click="handleCompleteStage(stage)">完成</el-button>
                    <el-button v-if="stage.status === 'pending'" size="small" type="info" @click="handleSkipStage(stage)">跳过</el-button>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="未初始化阶段" />
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

          <!-- 实验日志 -->
          <el-card class="detail-card">
            <template #header>
              <div class="card-header">
                <span>📝 实验日志</span>
                <el-button size="small" type="primary" @click="showLogDialog = true">添加日志</el-button>
              </div>
            </template>
            <div v-if="logs.length > 0" class="logs-timeline">
              <div v-for="log in logs" :key="log.id" class="log-item">
                <div class="log-time">{{ formatTime(log.created_at) }}</div>
                <div class="log-content">
                  <el-tag :type="getLogType(log.log_type)" size="small">{{ log.log_type_label }}</el-tag>
                  <span v-if="log.title" class="log-title">{{ log.title }}</span>
                  <p>{{ log.content }}</p>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无日志" />
          </el-card>

          <!-- 备注 -->
          <el-card v-if="experiment.notes" class="detail-card">
            <template #header><span>📝 备注</span></template>
            <p>{{ experiment.notes }}</p>
          </el-card>
        </el-col>

        <el-col :span="8">
          <!-- 里程碑 -->
          <el-card class="detail-card">
            <template #header>
              <div class="card-header">
                <span>🎯 里程碑</span>
                <el-button size="small" type="primary" @click="showMilestoneDialog = true">添加</el-button>
              </div>
            </template>
            <div v-if="milestones.length > 0" class="milestones-list">
              <div v-for="milestone in milestones" :key="milestone.id" class="milestone-item" :class="{ completed: milestone.status === 'completed', overdue: milestone.is_overdue }">
                <div class="milestone-header">
                  <el-checkbox :model-value="milestone.status === 'completed'" @change="handleCompleteMilestone(milestone)" />
                  <span class="milestone-title">{{ milestone.title }}</span>
                  <el-tag :type="getPriorityType(milestone.priority)" size="small">{{ milestone.priority }}</el-tag>
                </div>
                <div class="milestone-meta">
                  <span v-if="milestone.target_date">目标: {{ formatDate(milestone.target_date) }}</span>
                  <span v-if="milestone.completed_date">完成: {{ formatDate(milestone.completed_date) }}</span>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无里程碑" :image-size="60" />
          </el-card>

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

      <!-- 添加日志对话框 -->
      <el-dialog v-model="showLogDialog" title="添加实验日志" width="500px">
        <el-form :model="logForm" label-width="80px">
          <el-form-item label="标题">
            <el-input v-model="logForm.title" placeholder="日志标题（可选）" />
          </el-form-item>
          <el-form-item label="内容" required>
            <el-input v-model="logForm.content" type="textarea" :rows="4" placeholder="记录实验进展、问题、发现等" />
          </el-form-item>
          <el-form-item label="类型">
            <el-select v-model="logForm.log_type" style="width: 100%;">
              <el-option label="信息" value="info" />
              <el-option label="警告" value="warning" />
              <el-option label="错误" value="error" />
              <el-option label="里程碑" value="milestone" />
            </el-select>
          </el-form-item>
          <el-form-item label="关联阶段">
            <el-select v-model="logForm.stage_name" clearable placeholder="选择阶段" style="width: 100%;">
              <el-option v-for="stage in stages" :key="stage.id" :label="stage.stage_label" :value="stage.stage_name" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showLogDialog = false">取消</el-button>
          <el-button type="primary" :loading="logLoading" @click="handleCreateLog">添加</el-button>
        </template>
      </el-dialog>

      <!-- 添加里程碑对话框 -->
      <el-dialog v-model="showMilestoneDialog" title="添加里程碑" width="500px">
        <el-form :model="milestoneForm" label-width="80px">
          <el-form-item label="标题" required>
            <el-input v-model="milestoneForm.title" placeholder="里程碑标题" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="milestoneForm.description" type="textarea" :rows="2" placeholder="详细描述" />
          </el-form-item>
          <el-form-item label="目标日期">
            <el-date-picker v-model="milestoneForm.target_date" type="date" placeholder="选择日期" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="优先级">
            <el-select v-model="milestoneForm.priority" style="width: 100%;">
              <el-option label="低" value="low" />
              <el-option label="中" value="medium" />
              <el-option label="高" value="high" />
              <el-option label="紧急" value="critical" />
            </el-select>
          </el-form-item>
          <el-form-item label="关联阶段">
            <el-select v-model="milestoneForm.stage_name" clearable placeholder="选择阶段" style="width: 100%;">
              <el-option v-for="stage in stages" :key="stage.id" :label="stage.stage_label" :value="stage.stage_name" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showMilestoneDialog = false">取消</el-button>
          <el-button type="primary" :loading="milestoneLoading" @click="handleCreateMilestone">添加</el-button>
        </template>
      </el-dialog>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { experimentApi, audioApi, metricApi, stageApi, logApi, milestoneApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()

const experiment = ref<any>(null)
const audioFiles = ref<any[]>([])
const metricsSummary = ref<any>({})
const stages = ref<any[]>([])
const logs = ref<any[]>([])
const milestones = ref<any[]>([])
const loading = ref(false)

const showLogDialog = ref(false)
const logLoading = ref(false)
const logForm = reactive({
  title: '',
  content: '',
  log_type: 'info',
  stage_name: ''
})

const showMilestoneDialog = ref(false)
const milestoneLoading = ref(false)
const milestoneForm = reactive({
  title: '',
  description: '',
  target_date: '',
  priority: 'medium',
  stage_name: ''
})

const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
}))

function getStatusType(status: string) {
  const types: Record<string, string> = { planning: 'info', running: 'warning', completed: 'success', failed: 'danger', pending: 'info', in_progress: 'warning', skipped: 'info' }
  return types[status] || 'info'
}

function getStatusLabel(status: string) {
  const labels: Record<string, string> = { planning: '规划中', running: '进行中', completed: '已完成', failed: '已失败', pending: '待开始', in_progress: '进行中', skipped: '已跳过' }
  return labels[status] || status
}

function getLogType(type: string) {
  const types: Record<string, string> = { info: 'info', warning: 'warning', error: 'danger', milestone: 'success', debug: 'info' }
  return types[type] || 'info'
}

function getPriorityType(priority: string) {
  const types: Record<string, string> = { low: 'info', medium: '', high: 'warning', critical: 'danger' }
  return types[priority] || ''
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function formatTime(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleTimeString('zh-CN')
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
    stages.value = await stageApi.getList(id) as any
    const logsRes: any = await logApi.getList(id)
    logs.value = logsRes.logs || []
    milestones.value = await milestoneApi.getList(id) as any
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

async function handleInitStages() {
  try {
    await stageApi.initStages(experiment.value.id)
    ElMessage.success('阶段初始化成功')
    loadExperiment()
  } catch (e) {}
}

async function handleStartStage(stage: any) {
  try {
    await stageApi.start(stage.id)
    ElMessage.success('阶段已开始')
    loadExperiment()
  } catch (e) {}
}

async function handleCompleteStage(stage: any) {
  try {
    await stageApi.complete(stage.id)
    ElMessage.success('阶段已完成')
    loadExperiment()
  } catch (e) {}
}

async function handleSkipStage(stage: any) {
  try {
    await stageApi.skip(stage.id)
    ElMessage.success('阶段已跳过')
    loadExperiment()
  } catch (e) {}
}

async function handleCreateLog() {
  if (!logForm.content.trim()) return
  logLoading.value = true
  try {
    await logApi.create(experiment.value.id, logForm)
    showLogDialog.value = false
    logForm.title = ''
    logForm.content = ''
    logForm.log_type = 'info'
    logForm.stage_name = ''
    loadExperiment()
    ElMessage.success('日志添加成功')
  } catch (e) {} finally {
    logLoading.value = false
  }
}

async function handleCreateMilestone() {
  if (!milestoneForm.title.trim()) return
  milestoneLoading.value = true
  try {
    await milestoneApi.create(experiment.value.id, milestoneForm)
    showMilestoneDialog.value = false
    milestoneForm.title = ''
    milestoneForm.description = ''
    milestoneForm.target_date = ''
    milestoneForm.priority = 'medium'
    milestoneForm.stage_name = ''
    loadExperiment()
    ElMessage.success('里程碑添加成功')
  } catch (e) {} finally {
    milestoneLoading.value = false
  }
}

async function handleCompleteMilestone(milestone: any) {
  try {
    await milestoneApi.complete(milestone.id)
    ElMessage.success('里程碑已完成')
    loadExperiment()
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
  max-width: 1400px;
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.json-block {
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  font-size: 13px;
  overflow-x: auto;
  font-family: 'Consolas', monospace;
}

/* 阶段样式 */
.stages-container {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.stage-item {
  position: relative;
  display: flex;
  align-items: flex-start;
}

.stage-connector {
  position: absolute;
  left: 20px;
  top: 40px;
  bottom: -20px;
  width: 2px;
  background-color: #e4e7ed;
}

.connector-line {
  height: 100%;
  width: 100%;
}

.connector-line.active {
  background-color: #67c23a;
}

.stage-node {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 12px;
  background: #f9f9f9;
  width: 100%;
}

.stage-node.completed {
  background: #f0f9eb;
}

.stage-node.in_progress {
  background: #fdf6ec;
}

.stage-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #666;
}

.stage-node.completed .stage-icon {
  background: #67c23a;
  color: #fff;
}

.stage-node.in_progress .stage-icon {
  background: #e6a23c;
  color: #fff;
}

.stage-info {
  flex: 1;
}

.stage-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.stage-status {
  font-size: 12px;
  color: #999;
}

.stage-actions {
  display: flex;
  gap: 8px;
}

/* 日志样式 */
.logs-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.log-item {
  display: flex;
  gap: 16px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
}

.log-time {
  font-size: 12px;
  color: #999;
  min-width: 80px;
}

.log-content {
  flex: 1;
}

.log-title {
  font-weight: 600;
  margin-left: 8px;
}

.log-content p {
  margin-top: 8px;
  color: #555;
}

/* 里程碑样式 */
.milestones-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.milestone-item {
  padding: 12px;
  border-radius: 8px;
  background: #f9f9f9;
}

.milestone-item.completed {
  background: #f0f9eb;
  opacity: 0.7;
}

.milestone-item.overdue {
  background: #fef0f0;
}

.milestone-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.milestone-title {
  flex: 1;
  font-weight: 500;
}

.milestone-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 16px;
}

/* 音频样式 */
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

/* 指标样式 */
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