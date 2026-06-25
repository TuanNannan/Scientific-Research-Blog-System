<template>
  <div class="profile-page">
    <el-card class="profile-card">
      <div class="profile-header">
        <el-avatar :size="80" :src="userStore.user?.avatar">
          {{ userStore.user?.username?.charAt(0)?.toUpperCase() }}
        </el-avatar>
        <div class="profile-info">
          <h2>{{ userStore.user?.username }}</h2>
          <p>{{ userStore.user?.email }}</p>
          <el-tag>{{ userStore.user?.role }}</el-tag>
        </div>
      </div>

      <el-divider />

      <el-form :model="form" label-width="80px" style="max-width: 500px;">
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="个人简介">
          <el-input v-model="form.bio" type="textarea" :rows="3" placeholder="介绍一下你的研究方向..." />
        </el-form-item>
        <el-form-item label="头像URL">
          <el-input v-model="form.avatar" placeholder="头像图片链接" />
        </el-form-item>
        <el-divider content-position="left">修改密码</el-divider>
        <el-form-item label="新密码">
          <el-input v-model="form.password" type="password" placeholder="留空则不修改" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSave">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { userApi } from '@/api'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const loading = ref(false)

const form = reactive({
  email: '',
  bio: '',
  avatar: '',
  password: '',
})

onMounted(() => {
  if (userStore.user) {
    form.email = userStore.user.email || ''
    form.bio = userStore.user.bio || ''
    form.avatar = userStore.user.avatar || ''
  }
})

async function handleSave() {
  loading.value = true
  try {
    const data: any = {
      email: form.email,
      bio: form.bio,
      avatar: form.avatar,
    }
    if (form.password) {
      data.password = form.password
    }
    await userApi.updateMe(data)
    await userStore.fetchUser()
    ElMessage.success('保存成功')
    form.password = ''
  } catch (e) {} finally {
    loading.value = false
  }
}
</script>

<style scoped>
.profile-page {
  max-width: 800px;
  margin: 0 auto;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
}

.profile-info h2 {
  font-size: 24px;
  margin-bottom: 4px;
}

.profile-info p {
  color: #666;
  margin-bottom: 8px;
}
</style>