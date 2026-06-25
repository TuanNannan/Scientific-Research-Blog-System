import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        {
          path: '',
          name: 'Home',
          component: () => import('@/views/Home.vue'),
        },
        {
          path: 'blog',
          name: 'BlogList',
          component: () => import('@/views/blog/BlogList.vue'),
        },
        {
          path: 'blog/:id',
          name: 'BlogDetail',
          component: () => import('@/views/blog/BlogDetail.vue'),
        },
        {
          path: 'blog/write',
          name: 'BlogWrite',
          component: () => import('@/views/blog/BlogWrite.vue'),
        },
        {
          path: 'experiments',
          name: 'ExperimentList',
          component: () => import('@/views/experiment/ExperimentList.vue'),
        },
        {
          path: 'experiments/:id',
          name: 'ExperimentDetail',
          component: () => import('@/views/experiment/ExperimentDetailNew.vue'),
        },
        {
          path: 'todos',
          name: 'TodoList',
          component: () => import('@/views/todo/TodoList.vue'),
        },
        {
          path: 'profile',
          name: 'Profile',
          component: () => import('@/views/Profile.vue'),
        },
      ],
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue'),
    },
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const publicPages = ['/login', '/register']
  const authRequired = !publicPages.includes(to.path)

  if (authRequired && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router