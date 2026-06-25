<template>
  <div class="home-page">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-text">
        <h1>欢迎回来，{{ userStore.user?.username }} 👋</h1>
        <p>构音障碍语音识别科研博客系统 —— 记录你的科研旅程</p>
      </div>
      <div class="quick-actions">
        <el-button type="primary" @click="router.push('/blog/write')">
          <el-icon><EditPen /></el-icon> 写文章
        </el-button>
        <el-button @click="router.push('/experiments')">
          <el-icon><DataAnalysis /></el-icon> 新建实验
        </el-button>
        <el-button @click="router.push('/todos')">
          <el-icon><Plus /></el-icon> 新待办
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background-color: #e6f7ff;">
            <el-icon :size="28" color="#1890ff"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.posts }}</div>
            <div class="stat-label">博客文章</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background-color: #f6ffed;">
            <el-icon :size="28" color="#52c41a"><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.experiments }}</div>
            <div class="stat-label">实验记录</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background-color: #fff7e6;">
            <el-icon :size="28" color="#fa8c16"><Microphone /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.audioFiles }}</div>
            <div class="stat-label">音频文件</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background-color: #fff1f0;">
            <el-icon :size="28" color="#f5222d"><Finished /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.todos }}</div>
            <div class="stat-label">待办事项</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 最近文章 -->
      <el-col :span="12">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>📝 最近文章</span>
              <el-button text @click="router.push('/blog')">查看全部</el-button>
            </div>
          </template>
          <div v-if="recentPosts.length" class="recent-list">
            <div v-for="post in recentPosts" :key="post.id" class="recent-item" @click="router.push(`/blog/${post.id}`)">
              <div class="item-title">{{ post.title }}</div>
              <div class="item-meta">
                <span>{{ post.category || '未分类' }}</span>
                <span>{{ formatDate(post.created_at) }}</span>
              </div>
            </div>
          </div>
          <el-empty v-else description="还没有文章" />
        </el-card>
      </el-col>

      <!-- 最近实验 -->
      <el-col :span="12">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>🔬 最近实验</span>
              <el-button text @click="router.push('/experiments')">查看全部</el-button>
            </div>
          </template>
          <div v-if="recentExperiments.length" class="recent-list">
            <div v-for="exp in recentExperiments" :key="exp.id" class="recent-item" @click="router.push(`/experiments/${exp.id}`)">
              <div class="item-title">{{ exp.title }}</div>
              <div class="item-meta">
                <el-tag :type="getStatusType(exp.status)" size="small">{{ exp.status }}</el-tag>
                <span>{{ formatDate(exp.created_at) }}</span>
              </div>
            </div>
          </div>
          <el-empty v-else description="还没有实验" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { postApi, experimentApi, audioApi, todoApi } from '@/api'

const router = useRouter()
const userStore = useUserStore()

const stats = ref({
  posts: 0,
  experiments: 0,
  audioFiles: 0,
  todos: 0,
})

const recentPosts = ref<any[]>([])
const recentExperiments = ref<any[]>([])

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

function getStatusType(status: string) {
  const types: Record<string, string> = {
    planning: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return types[status] || 'info'
}

async function loadData() {
  try {
    const [postsRes, expsRes, audioRes, todoRes] = await Promise.all([
      postApi.getList({ per_page: 5 }),
      experimentApi.getList({ per_page: 5 }),
      audioApi.getStats(),
      todoApi.getStats(),
    ])

    stats.value.posts = (postsRes as any).total || 0
    stats.value.experiments = (expsRes as any).total || 0
    stats.value.audioFiles = (audioRes as any).total_files || 0
    stats.value.todos = (todoRes as any).total || 0
    recentPosts.value = (postsRes as any).posts || []
    recentExperiments.value = (expsRes as any).experiments || []
  } catch (e) {
    console.error('加载数据失败', e)
  }
}

onMounted(loadData)
</script>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  background: linear-gradient(135deg, #1890ff, #722ed1);
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
}

.welcome-text h1 {
  font-size: 24px;
  margin-bottom: 8px;
}

.welcome-text p {
  opacity: 0.85;
  font-size: 14px;
}

.quick-actions {
  display: flex;
  gap: 12px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #333;
}

.stat-label {
  font-size: 13px;
  color: #999;
}

.section-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.recent-item:hover {
  background-color: #f5f7fa;
}

.item-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}
</style>