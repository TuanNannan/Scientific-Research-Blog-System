<template>
  <div class="todo-list">
    <div class="list-header">
      <div class="filters">
        <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 120px;">
          <el-option label="待办" value="pending" />
          <el-option label="进行中" value="in_progress" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <el-select v-model="priorityFilter" placeholder="优先级" clearable style="width: 120px;">
          <el-option label="紧急" value="urgent" />
          <el-option label="高" value="high" />
          <el-option label="中" value="medium" />
          <el-option label="低" value="low" />
        </el-select>
      </div>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon> 新建待办
      </el-button>
    </div>

    <!-- 统计 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4" v-for="item in statItems" :key="item.label">
        <el-card shadow="hover" class="mini-stat" :body-style="{ padding: '16px', textAlign: 'center' }">
          <div class="stat-num" :style="{ color: item.color }">{{ stats[item.key] || 0 }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 待办列表 -->
    <el-card class="todo-card">
      <div v-for="todo in todos" :key="todo.id" class="todo-item" :class="{ completed: todo.status === 'completed' }">
        <div class="todo-left">
          <el-checkbox :model-value="todo.status === 'completed'" @change="toggleComplete(todo)" />
          <div class="todo-content">
            <div class="todo-title" :class="{ 'line-through': todo.status === 'completed' }">
              {{ todo.title }}
            </div>
            <div class="todo-meta">
              <el-tag :type="getPriorityType(todo.priority)" size="small">{{ getPriorityLabel(todo.priority) }}</el-tag>
              <span v-if="todo.category" class="category">{{ todo.category }}</span>
              <span v-if="todo.due_date" class="due-date" :class="{ overdue: isOverdue(todo) }">
                <el-icon><Calendar /></el-icon> {{ formatDate(todo.due_date) }}
              </span>
            </div>
          </div>
        </div>
        <div class="todo-right">
          <el-tag v-for="tag in (todo.tags || [])" :key="tag.tag || tag" size="small" type="info" effect="plain">
            {{ tag.tag || tag }}
          </el-tag>
          <el-button text type="danger" size="small" @click="handleDelete(todo.id)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
      <el-empty v-if="todos.length === 0 && !loading" description="暂无待办事项" />
    </el-card>

    <!-- 新建对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建待办事项" width="500px">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="createForm.title" placeholder="待办事项标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" :rows="2" placeholder="详细描述（可选）" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="分类">
              <el-input v-model="createForm.category" placeholder="如：实验、论文" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="createForm.priority" style="width: 100%;">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="紧急" value="urgent" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="截止日期">
          <el-date-picker v-model="createForm.due_date" type="date" placeholder="选择日期" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="createForm.tags" multiple filterable allow-create placeholder="输入标签后回车" style="width: 100%;" />
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
import { todoApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const todos = ref<any[]>([])
const loading = ref(false)
const statusFilter = ref('')
const priorityFilter = ref('')
const showCreateDialog = ref(false)
const createLoading = ref(false)

const stats = ref<any>({})
const statItems = [
  { key: 'total', label: '总计', color: '#333' },
  { key: 'pending', label: '待办', color: '#1890ff' },
  { key: 'in_progress', label: '进行中', color: '#fa8c16' },
  { key: 'completed', label: '已完成', color: '#52c41a' },
  { key: 'cancelled', label: '已取消', color: '#999' },
  { key: 'overdue', label: '已过期', color: '#f5222d' },
]

const createForm = reactive({
  title: '',
  description: '',
  category: '',
  priority: 'medium',
  due_date: '',
  tags: [] as string[],
})

function getPriorityType(priority: string) {
  const types: Record<string, string> = { low: 'info', medium: '', high: 'warning', urgent: 'danger' }
  return types[priority] || ''
}

function getPriorityLabel(priority: string) {
  const labels: Record<string, string> = { low: '低', medium: '中', high: '高', urgent: '紧急' }
  return labels[priority] || priority
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function isOverdue(todo: any) {
  return todo.due_date && new Date(todo.due_date) < new Date() && todo.status !== 'completed'
}

async function loadTodos() {
  loading.value = true
  try {
    const params: any = { per_page: 50 }
    if (statusFilter.value) params.status = statusFilter.value
    if (priorityFilter.value) params.priority = priorityFilter.value
    const res: any = await todoApi.getList(params)
    todos.value = res.todos || []
  } catch (e) {} finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    stats.value = await todoApi.getStats() as any
  } catch (e) {}
}

async function handleCreate() {
  if (!createForm.title.trim()) return
  createLoading.value = true
  try {
    await todoApi.create(createForm)
    showCreateDialog.value = false
    createForm.title = ''
    createForm.description = ''
    createForm.category = ''
    createForm.priority = 'medium'
    createForm.due_date = ''
    createForm.tags = []
    loadTodos()
    loadStats()
    ElMessage.success('创建成功')
  } catch (e) {} finally {
    createLoading.value = false
  }
}

async function toggleComplete(todo: any) {
  try {
    if (todo.status === 'completed') {
      // 取消完成，暂不支持
    } else {
      await todoApi.complete(todo.id)
      ElMessage.success('已完成')
    }
    loadTodos()
    loadStats()
  } catch (e) {}
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定要删除这个待办事项吗？', '确认删除', { type: 'warning' })
  try {
    await todoApi.delete(id)
    ElMessage.success('删除成功')
    loadTodos()
    loadStats()
  } catch (e) {}
}

watch([statusFilter, priorityFilter], loadTodos)
onMounted(() => { loadTodos(); loadStats() })
</script>

<style scoped>
.todo-list {
  max-width: 1000px;
  margin: 0 auto;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filters {
  display: flex;
  gap: 12px;
}

.stats-row {
  margin-bottom: 24px;
}

.mini-stat {
  cursor: pointer;
  transition: transform 0.2s;
}

.mini-stat:hover {
  transform: translateY(-2px);
}

.stat-num {
  font-size: 28px;
  font-weight: 700;
}

.stat-label {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.todo-card {
  margin-bottom: 24px;
}

.todo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.todo-item:hover {
  background-color: #f9f9f9;
}

.todo-item:last-child {
  border-bottom: none;
}

.todo-item.completed {
  opacity: 0.6;
}

.todo-left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex: 1;
}

.todo-content {
  flex: 1;
}

.todo-title {
  font-size: 15px;
  font-weight: 500;
  color: #333;
  margin-bottom: 6px;
}

.todo-title.line-through {
  text-decoration: line-through;
  color: #999;
}

.todo-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  font-size: 12px;
  color: #999;
}

.category {
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 4px;
}

.due-date {
  display: flex;
  align-items: center;
  gap: 4px;
}

.due-date.overdue {
  color: #f5222d;
}

.todo-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>