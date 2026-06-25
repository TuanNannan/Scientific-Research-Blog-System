<template>
  <div class="experiment-list">
    <div class="list-header">
      <div class="filters">
        <el-select v-model="statusFilter" placeholder="实验状态" clearable style="width: 150px;">
          <el-option label="规划中" value="planning" />
          <el-option label="进行中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="已失败" value="failed" />
        </el-select>
      </div>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon> 新建实验
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="stat-num" style="color: #1890ff;">{{ stats.planning }}</div>
          <div class="stat-label">规划中</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="stat-num" style="color: #fa8c16;">{{ stats.running }}</div>
          <div class="stat-label">进行中</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="stat-num" style="color: #52c41a;">{{ stats.completed }}</div>
          <div class="stat-label">已完成</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="stat-num" style="color: #f5222d;">{{ stats.failed }}</div>
          <div class="stat-label">已失败</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实验列表 -->
    <div class="experiments-grid">
      <el-card v-for="exp in experiments" :key="exp.id" class="experiment-card" shadow="hover" @click="router.push(`/experiments/${exp.id}`)">
        <div class="card-header">
          <el-tag :type="getStatusType(exp.status)" size="small">{{ getStatusLabel(exp.status) }}</el-tag>
          <span class="date">{{ formatDate(exp.created_at) }}</span>
        </div>
        <h3 class="card-title">{{ exp.title }}</h3>
        <p class="card-desc">{{ exp.description || '暂无描述' }}</p>
        <div class="card-info">
          <span v-if="exp.model_architecture">
            <el-icon><Cpu /></el-icon> {{ exp.model_architecture }}
          </span>
          <span v-if="exp.framework">
            <el-icon><Monitor /></el-icon> {{ exp.framework }}
          </span>
        </div>
        <el-progress v-if="exp.status === 'running'" :percentage="exp.progress" :stroke-width="6" style="margin-top: 12px;" />
      </el-card>
    </div>

    <el-empty v-if="experiments.length === 0 && !loading" description="还没有实验记录">
      <el-button type="primary" @click="showCreateDialog = true">创建第一个实验</el-button>
    </el-empty>

    <!-- 新建实验对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建实验" width="500px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="实验标题" required>
          <el-input v-model="createForm.title" placeholder="如：CNN-LSTM模型训练 v1" />
        </el-form-item>
        <el-form-item label="实验描述">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="描述实验目标和内容" />
        </el-form-item>
        <el-form-item label="模型架构">
          <el-input v-model="createForm.model_architecture" placeholder="如：CNN, RNN, Transformer" />
        </el-form-item>
        <el-form-item label="深度学习框架">
          <el-select v-model="createForm.framework" placeholder="选择框架">
            <el-option label="PyTorch" value="PyTorch" />
            <el-option label="TensorFlow" value="TensorFlow" />
            <el-option label="Keras" value="Keras" />
            <el-option label="其他" value="Other" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { experimentApi } from '@/api'

const router = useRouter()

const experiments = ref<any[]>([])
const loading = ref(false)
const statusFilter = ref('')
const showCreateDialog = ref(false)
const createLoading = ref(false)

const stats = ref({ planning: 0, running: 0, completed: 0, failed: 0, total: 0 })

const createForm = reactive({
  title: '',
  description: '',
  model_architecture: '',
  framework: '',
})

function getStatusType(status: string) {
  const types: Record<string, string> = { planning: 'info', running: 'warning', completed: 'success', failed: 'danger' }
  return types[status] || 'info'
}

function getStatusLabel(status: string) {
  const labels: Record<string, string> = { planning: '规划中', running: '进行中', completed: '已完成', failed: '已失败' }
  return labels[status] || status
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

async function loadExperiments() {
  loading.value = true
  try {
    const params: any = { per_page: 20 }
    if (statusFilter.value) params.status = statusFilter.value
    const res: any = await experimentApi.getList(params)
    experiments.value = res.experiments || []
  } catch (e) {} finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    const res: any = await experimentApi.getStats()
    stats.value = res
  } catch (e) {}
}

async function handleCreate() {
  if (!createForm.title.trim()) return
  createLoading.value = true
  try {
    await experimentApi.create(createForm)
    showCreateDialog.value = false
    createForm.title = ''
    createForm.description = ''
    createForm.model_architecture = ''
    createForm.framework = ''
    loadExperiments()
    loadStats()
  } catch (e) {} finally {
    createLoading.value = false
  }
}

watch(statusFilter, loadExperiments)
onMounted(() => { loadExperiments(); loadStats() })
</script>

<style scoped>
.experiment-list {
  max-width: 1200px;
  margin: 0 auto;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 24px;
}

.mini-stat {
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.mini-stat:hover {
  transform: translateY(-2px);
}

.stat-num {
  font-size: 32px;
  font-weight: 700;
}

.stat-label {
  font-size: 13px;
  color: #999;
  margin-top: 4px;
}

.experiments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.experiment-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.experiment-card:hover {
  transform: translateY(-4px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.date {
  font-size: 12px;
  color: #999;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.card-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-info {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #999;
}

.card-info span {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>