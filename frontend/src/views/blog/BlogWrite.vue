<template>
  <div class="blog-write">
    <div class="write-header">
      <el-button text @click="router.push('/blog')">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <h2>{{ isEdit ? '编辑文章' : '写新文章' }}</h2>
      <div class="header-actions">
        <el-button @click="saveDraft">保存草稿</el-button>
        <el-button type="primary" @click="publish">发布文章</el-button>
      </div>
    </div>

    <el-form :model="form" label-position="top" class="write-form">
      <el-form-item>
        <el-input v-model="form.title" placeholder="输入文章标题..." class="title-input" />
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="分类">
            <el-input v-model="form.category" placeholder="如：论文笔记、实验报告" />
          </el-form-item>
        </el-col>
        <el-col :span="16">
          <el-form-item label="标签">
            <el-select v-model="form.tags" multiple filterable allow-create placeholder="输入标签后回车" style="width: 100%;">
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="摘要">
        <el-input v-model="form.summary" type="textarea" :rows="2" placeholder="文章摘要（可选）" />
      </el-form-item>

      <el-form-item label="正文内容（支持Markdown）">
        <el-input v-model="form.content" type="textarea" :rows="20" placeholder="在这里写下你的文章内容..." class="content-textarea" />
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postApi } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const editId = ref<number | null>(null)

const form = reactive({
  title: '',
  content: '',
  summary: '',
  category: '',
  tags: [] as string[],
  status: 'draft',
})

async function loadPost() {
  const id = route.query.id
  if (id) {
    try {
      const post: any = await postApi.getOne(Number(id))
      isEdit.value = true
      editId.value = Number(id)
      form.title = post.title
      form.content = post.content
      form.summary = post.summary || ''
      form.category = post.category || ''
      form.tags = post.tags || []
      form.status = post.status
    } catch (e) {
      ElMessage.error('加载文章失败')
    }
  }
}

async function saveDraft() {
  form.status = 'draft'
  await save()
}

async function publish() {
  if (!form.title.trim() || !form.content.trim()) {
    ElMessage.warning('标题和内容不能为空')
    return
  }
  form.status = 'published'
  await save()
}

async function save() {
  try {
    if (isEdit.value && editId.value) {
      await postApi.update(editId.value, form)
      ElMessage.success('更新成功')
    } else {
      const res: any = await postApi.create(form)
      ElMessage.success('创建成功')
      editId.value = res.post.id
      isEdit.value = true
    }
    router.push('/blog')
  } catch (e) {}
}

onMounted(loadPost)
</script>

<style scoped>
.blog-write {
  max-width: 900px;
  margin: 0 auto;
}

.write-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.write-header h2 {
  font-size: 20px;
  color: #333;
}

.title-input :deep(.el-input__inner) {
  font-size: 24px;
  font-weight: 600;
  border: none;
  padding: 12px 0;
}

.content-textarea :deep(.el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.8;
}

.write-form {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}
</style>