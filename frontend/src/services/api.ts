import axios from 'axios'
import { AnalysisResult, KnowledgeItem, ModelConfig } from '@/types'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const analyzeConversation = async (
  text?: string,
  imageBase64?: string,
  context?: string
): Promise<AnalysisResult> => {
  const response = await api.post('/analysis/analyze', {
    text,
    image_base64: imageBase64,
    context,
  })
  return response.data
}

export const getKnowledgeItems = async (
  skip = 0,
  limit = 20,
  category?: string,
  search?: string
): Promise<KnowledgeItem[]> => {
  const params = new URLSearchParams()
  params.append('skip', skip.toString())
  params.append('limit', limit.toString())
  if (category) params.append('category', category)
  if (search) params.append('search', search)
  
  const response = await api.get(`/knowledge/?${params.toString()}`)
  return response.data
}

export const createKnowledgeItem = async (
  item: Omit<KnowledgeItem, 'id' | 'created_at'>
): Promise<KnowledgeItem> => {
  const response = await api.post('/knowledge/', item)
  return response.data
}

export const deleteKnowledgeItem = async (id: number): Promise<void> => {
  await api.delete(`/knowledge/${id}`)
}

export const getCategories = async (): Promise<{ name: string; count: number }[]> => {
  const response = await api.get('/knowledge/categories/list')
  return response.data
}

export const getModelConfigs = async (): Promise<ModelConfig[]> => {
  const response = await api.get('/config/')
  return response.data
}

export const activateModel = async (provider: string): Promise<void> => {
  await api.post(`/config/${provider}/activate`)
}

export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await api.get('/health')
  return response.data
}

export default api
