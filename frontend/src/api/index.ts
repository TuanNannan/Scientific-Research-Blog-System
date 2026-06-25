import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.error || '请求失败'
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    } else {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

// 用户API
export const userApi = {
  login: (data: { username: string; password: string }) =>
    api.post('/users/login', data),
  register: (data: { username: string; email: string; password: string }) =>
    api.post('/users/register', data),
  getMe: () => api.get('/users/me'),
  updateMe: (data: any) => api.put('/users/me', data),
}

// 博客API
export const postApi = {
  getList: (params?: { page?: number; per_page?: number; category?: string; tag?: string }) =>
    api.get('/posts', { params }),
  getOne: (id: number) => api.get(`/posts/${id}`),
  create: (data: any) => api.post('/posts', data),
  update: (id: number, data: any) => api.put(`/posts/${id}`, data),
  delete: (id: number) => api.delete(`/posts/${id}`),
  like: (id: number) => api.post(`/posts/${id}/like`),
  getComments: (id: number) => api.get(`/posts/${id}/comments`),
  createComment: (id: number, data: any) => api.post(`/posts/${id}/comments`, data),
  getCategories: () => api.get('/posts/categories'),
  getTags: () => api.get('/posts/tags'),
}

// 实验API
export const experimentApi = {
  getList: (params?: { page?: number; per_page?: number; status?: string }) =>
    api.get('/experiments', { params }),
  getOne: (id: number) => api.get(`/experiments/${id}`),
  create: (data: any) => api.post('/experiments', data),
  update: (id: number, data: any) => api.put(`/experiments/${id}`, data),
  delete: (id: number) => api.delete(`/experiments/${id}`),
  start: (id: number) => api.post(`/experiments/${id}/start`),
  complete: (id: number, data?: any) => api.post(`/experiments/${id}/complete`, data),
  fail: (id: number, data?: any) => api.post(`/experiments/${id}/fail`, data),
  updateProgress: (id: number, progress: number) =>
    api.put(`/experiments/${id}/progress`, { progress }),
  getStats: () => api.get('/experiments/stats'),
}

// 音频文件API
export const audioApi = {
  getList: (experimentId: number) => api.get(`/experiments/${experimentId}/audio`),
  upload: (experimentId: number, formData: FormData) =>
    api.post(`/experiments/${experimentId}/audio`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getOne: (id: number) => api.get(`/audio/${id}`),
  update: (id: number, data: any) => api.put(`/audio/${id}`, data),
  delete: (id: number) => api.delete(`/audio/${id}`),
  getStats: () => api.get('/audio/stats'),
}

// 实验指标API
export const metricApi = {
  getList: (experimentId: number, params?: { metric_name?: string; phase?: string }) =>
    api.get(`/experiments/${experimentId}/metrics`, { params }),
  create: (experimentId: number, data: any) =>
    api.post(`/experiments/${experimentId}/metrics`, data),
  createBatch: (experimentId: number, metrics: any[]) =>
    api.post(`/experiments/${experimentId}/metrics/batch`, { metrics }),
  getSummary: (experimentId: number) =>
    api.get(`/experiments/${experimentId}/metrics/summary`),
  getTimeline: (experimentId: number, metricName: string) =>
    api.get(`/experiments/${experimentId}/metrics/timeline`, { params: { metric_name: metricName } }),
}

// 待办事项API
export const todoApi = {
  getList: (params?: { page?: number; per_page?: number; status?: string; category?: string; priority?: string }) =>
    api.get('/todos', { params }),
  getOne: (id: number) => api.get(`/todos/${id}`),
  create: (data: any) => api.post('/todos', data),
  update: (id: number, data: any) => api.put(`/todos/${id}`, data),
  delete: (id: number) => api.delete(`/todos/${id}`),
  complete: (id: number) => api.post(`/todos/${id}/complete`),
  cancel: (id: number) => api.post(`/todos/${id}/cancel`),
  getStats: () => api.get('/todos/stats'),
  getCategories: () => api.get('/todos/categories'),
  getOverdue: () => api.get('/todos/overdue'),
}

// 实验阶段API
export const stageApi = {
  getList: (experimentId: number) =>
    api.get(`/experiments/${experimentId}/stages`),
  initStages: (experimentId: number) =>
    api.post(`/experiments/${experimentId}/stages/init`),
  getOne: (id: number) => api.get(`/stages/${id}`),
  update: (id: number, data: any) => api.put(`/stages/${id}`, data),
  delete: (id: number) => api.delete(`/stages/${id}`),
  start: (id: number) => api.post(`/stages/${id}/start`),
  complete: (id: number) => api.post(`/stages/${id}/complete`),
  skip: (id: number) => api.post(`/stages/${id}/skip`),
  updateProgress: (id: number, progress: number) =>
    api.put(`/stages/${id}/progress`, { progress }),
}

// 实验日志API
export const logApi = {
  getList: (experimentId: number, params?: { page?: number; per_page?: number; log_type?: string; stage_name?: string }) =>
    api.get(`/experiments/${experimentId}/logs`, { params }),
  create: (experimentId: number, data: any) =>
    api.post(`/experiments/${experimentId}/logs`, data),
  createBatch: (experimentId: number, logs: any[]) =>
    api.post(`/experiments/${experimentId}/logs/batch`, { logs }),
  getOne: (id: number) => api.get(`/logs/${id}`),
  update: (id: number, data: any) => api.put(`/logs/${id}`, data),
  delete: (id: number) => api.delete(`/logs/${id}`),
  getTimeline: (experimentId: number) =>
    api.get(`/experiments/${experimentId}/logs/timeline`),
}

// 实验里程碑API
export const milestoneApi = {
  getList: (experimentId: number, params?: { status?: string }) =>
    api.get(`/experiments/${experimentId}/milestones`, { params }),
  create: (experimentId: number, data: any) =>
    api.post(`/experiments/${experimentId}/milestones`, data),
  getOne: (id: number) => api.get(`/milestones/${id}`),
  update: (id: number, data: any) => api.put(`/milestones/${id}`, data),
  delete: (id: number) => api.delete(`/milestones/${id}`),
  complete: (id: number) => api.post(`/milestones/${id}/complete`),
  getOverdue: (experimentId: number) =>
    api.get(`/experiments/${experimentId}/milestones/overdue`),
  getStats: (experimentId: number) =>
    api.get(`/experiments/${experimentId}/milestones/stats`),
}

export default api