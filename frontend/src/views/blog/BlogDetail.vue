<template>
  <div class="blog-detail" v-loading="loading">
    <template v-if="post">
      <div class="detail-header">
        <el-button text @click="router.push('/blog')">
          <el-icon><ArrowLeft /></el-icon> 返回列表
        </el-button>
        <div class="header-actions" v-if="isAuthor">
          <el-button @click="router.push(`/blog/write?id=${post.id}`)">编辑</el-button>
          <el-button type="danger" @click="handleDelete">删除</el-button>
        </div>
      </div>

      <el-card class="article-card">
        <h1 class="article-title">{{ post.title }}</h1>
        <div class="article-meta">
          <span><el-icon><User /></el-icon> {{ post.author_name }}</span>
          <span><el-icon><Calendar /></el-icon> {{ formatDate(post.created_at) }}</span>
          <span><el-icon><View /></el-icon> {{ post.views_count }} 次浏览</span>
          <el-tag v-if="post.category" size="small">{{ post.category }}</el-tag>
        </div>
        <div class="article-tags" v-if="post.tags?.length">
          <el-tag v-for="tag in post.tags" :key="tag" type="info" effect="plain" size="small">{{ tag }}</el-tag>
        </div>
        <el-divider />
        <div class="article-content" v-html="renderedContent"></div>
        <div class="article-actions">
          <el-button :type="liked ? 'primary' : 'default'" @click="handleLike">
            <el-icon><Star /></el-icon> {{ post.likes_count }} 点赞
          </el-button>
        </div>
      </el-card>

      <!-- 评论区 -->
      <el-card class="comment-section">
        <template #header>
          <span>💬 评论 ({{ comments.length }})</span>
        </template>
        <div class="comment-input">
          <el-input v-model="newComment" type="textarea" :rows="3" placeholder="写下你的评论..." />
          <el-button type="primary" style="margin-top: 12px;" :loading="commentLoading" @click="submitComment">
            发表评论
          </el-button>
        </div>
        <el-divider />
        <div class="comment-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <el-avatar :size="36">{{ comment.author_name?.charAt(0) }}</el-avatar>
            <div class="comment-body">
              <div class="comment-header">
                <span class="comment-author">{{ comment.author_name }}</span>
                <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
              </div>
              <div class="comment-content">{{ comment.content }}</div>
            </div>
          </div>
          <el-empty v-if="comments.length === 0" description="暂无评论" />
        </div>
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postApi } from '@/api'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const post = ref<any>(null)
const comments = ref<any[]>([])
const loading = ref(false)
const commentLoading = ref(false)
const newComment = ref('')
const liked = ref(false)

const isAuthor = computed(() => post.value?.author_id === userStore.user?.id)

// 简易Markdown渲染（后续可用marked替换）
const renderedContent = computed(() => {
  if (!post.value?.content) return ''
  return post.value.content
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
})

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function loadPost() {
  loading.value = true
  try {
    const id = Number(route.params.id)
    post.value = await postApi.getOne(id)
    comments.value = await postApi.getComments(id) as any
  } catch (e) {
    ElMessage.error('加载文章失败')
  } finally {
    loading.value = false
  }
}

async function handleLike() {
  try {
    const res: any = await postApi.like(post.value.id)
    post.value.likes_count = res.likes_count
    liked.value = true
  } catch (e) {}
}

async function submitComment() {
  if (!newComment.value.trim()) return
  commentLoading.value = true
  try {
    const res: any = await postApi.createComment(post.value.id, { content: newComment.value })
    comments.value.unshift(res.comment)
    newComment.value = ''
    ElMessage.success('评论成功')
  } catch (e) {} finally {
    commentLoading.value = false
  }
}

async function handleDelete() {
  await ElMessageBox.confirm('确定要删除这篇文章吗？', '确认删除', { type: 'warning' })
  try {
    await postApi.delete(post.value.id)
    ElMessage.success('删除成功')
    router.push('/blog')
  } catch (e) {}
}

onMounted(loadPost)
</script>

<style scoped>
.blog-detail {
  max-width: 900px;
  margin: 0 auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.article-card {
  margin-bottom: 24px;
}

.article-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 16px;
}

.article-meta {
  display: flex;
  gap: 20px;
  color: #666;
  font-size: 14px;
  margin-bottom: 12px;
}

.article-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.article-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.article-content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  padding: 16px 0;
}

.article-actions {
  text-align: center;
  padding: 20px 0;
}

.comment-section {
  margin-bottom: 24px;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  display: flex;
  gap: 12px;
}

.comment-body {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment-author {
  font-weight: 600;
  color: #333;
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.comment-content {
  color: #555;
  line-height: 1.6;
}
</style>