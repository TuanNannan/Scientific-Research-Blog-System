<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo" @click="router.push('/')">
        <el-icon :size="24"><Microphone /></el-icon>
        <span v-show="!isCollapse" class="logo-text">科研博客</span>
      </div>

      <el-menu
        :default-active="route.path"
        :collapse="isCollapse"
        router
        class="side-menu"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <template #title>首页</template>
        </el-menu-item>

        <el-menu-item index="/blog">
          <el-icon><Document /></el-icon>
          <template #title>博客文章</template>
        </el-menu-item>

        <el-menu-item index="/experiments">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>实验记录</template>
        </el-menu-item>

        <el-menu-item index="/todos">
          <el-icon><Finished /></el-icon>
          <template #title>待办事项</template>
        </el-menu-item>
      </el-menu>

      <div class="collapse-btn" @click="isCollapse = !isCollapse">
        <el-icon>
          <Fold v-if="!isCollapse" />
          <Expand v-else />
        </el-icon>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h2 class="page-title">{{ pageTitle }}</h2>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click">
            <div class="user-info">
              <el-avatar :size="32" :src="userStore.user?.avatar">
                {{ userStore.user?.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span class="username">{{ userStore.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">
                  <el-icon><User /></el-icon> 个人资料
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isCollapse = ref(false)

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/': '首页',
    '/blog': '博客文章',
    '/experiments': '实验记录',
    '/todos': '待办事项',
    '/profile': '个人资料',
  }
  return titles[route.path] || '科研博客系统'
})

function handleLogout() {
  userStore.logout()
  router.push('/login')
}

onMounted(() => {
  if (userStore.isLoggedIn && !userStore.user) {
    userStore.fetchUser()
  }
})
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.aside {
  background-color: #001529;
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.side-menu {
  flex: 1;
  border-right: none;
  background-color: transparent;
}

.side-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.65);
}

.side-menu .el-menu-item:hover,
.side-menu .el-menu-item.is-active {
  color: #fff;
  background-color: #1890ff;
}

.collapse-btn {
  padding: 16px;
  text-align: center;
  color: rgba(255, 255, 255, 0.65);
  cursor: pointer;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.collapse-btn:hover {
  color: #fff;
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #333;
}

.main-content {
  background-color: #f5f7fa;
  padding: 24px;
  overflow-y: auto;
}
</style>