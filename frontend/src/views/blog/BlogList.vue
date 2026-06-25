<template>
  <div class="blog-list">
    <div class="list-header">
      <div class="filters">
        <el-input v-model="searchText" placeholder="搜索文章..." prefix-icon="Search" clearable style="width: 300px;" />
        <el-select v-model="selectedCategory" placeholder="选择分类" clearable style="width: 150px;">
          <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
        </el-select>
      </div>
      <el-button type="primary" @click="router.push('/blog/write')">
        <el-icon><EditPen /></el-icon> 写文章
      </el-button>
    </div>

    <div class="posts-grid">
      <el-card v-for="post in filteredPosts" :key="post.id" class="post-card" shadow="hover" @click="router.push(`/blog/${post.id}`)">
        <div class="post-header">
          <el-tag v-if="post.category" size="small">{{ post.category }}</el-tag>
          <span class="post-date">{{ formatDate(post.created_at) }}</span>
        </div>
        <h3 class="post-title">{{ post.title }}</h3>
        <p class="post-summary">{{ post.summary || truncate(post.content, 120) }}</p>
        <div class="post-footer">
          <div class="post-tags">
            <el-tag v-for="tag in (post.tags || []).slice(0, 3)" :key="tag" type="info" size="small" effect="plain">
              {{ tag }}
            </el-tag>
          </div>
          <div class="post-stats">
            <span><el-icon><View /></el-icon> {{ post.views_count }}</span>
            <span><el-icon><Star /></el-icon> {{ post.likes_count }}</span>
          </div>
        </div>
      </el-card>
    </div>

    <div v-if="!loading && posts.length === 0" class="empty-state">
      <el-empty description="还没有文章">
        <el-button type="primary" @click="router.push('/blog/write')">写第一篇文章</el-button>
      </el-empty>
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadPosts"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { postApi } from '@/api'

const router = useRouter()

const posts = ref<any[]>([])
const categories = ref<string[]>([])
const loading = ref(false)
const searchText = ref('')
const selectedCategory = ref('')
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const filteredPosts = computed(() => {
  return posts.value.filter((post) => {
    const matchSearch = !searchText.value || post.title.includes(searchText.value)
    const matchCategory = !selectedCategory.value || post.category === selectedCategory.value
    return matchSearch && matchCategory
  })
})

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function truncate(text: string, length: number) {
  if (!text) return ''
  return text.length > length ? text.slice(0, length) + '...' : text
}

async function loadPosts() {
  loading.value = true
  try {
    const res: any = await postApi.getList({ page: currentPage.value, per_page: pageSize.value })
    posts.value = res.posts || []
    total.value = res.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  try {
    const res: any = await postApi.getCategories()
    categories.value = res || []
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadPosts()
  loadCategories()
})
</script>

<style scoped>
.blog-list {
  max-width: 1200px;
  margin: 0 auto;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.filters {
  display: flex;
  gap: 12px;
}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.post-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.post-card:hover {
  transform: translateY(-4px);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.post-date {
  font-size: 12px;
  color: #999;
}

.post-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-summary {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.post-tags {
  display: flex;
  gap: 6px;
}

.post-stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #999;
}

.post-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}
</style>