import React, { useState, useEffect } from 'react'
import { 
  Brain, 
  Play, 
  Pause, 
  RefreshCw, 
  Plus, 
  Trash2, 
  Search,
  Loader2,
  CheckCircle,
  XCircle,
  Clock,
  Video,
  BookOpen
} from 'lucide-react'
import axios from 'axios'

const LEARNING_API = 'http://localhost:8002'

interface LearningTask {
  id: number
  platform: string
  keyword: string
  video_id: string | null
  video_url: string | null
  video_title: string | null
  video_author: string | null
  status: string
  error_message: string | null
  knowledge_extracted: boolean
  created_at: string
  completed_at: string | null
}

interface Keyword {
  id: number
  platform: string
  keyword: string
  is_active: boolean
  created_at: string
}

interface Statistics {
  total: number
  completed: number
  failed: number
  pending: number
  processing: number
  success_rate: number
}

export default function Learning() {
  const [tasks, setTasks] = useState<LearningTask[]>([])
  const [keywords, setKeywords] = useState<Keyword[]>([])
  const [stats, setStats] = useState<Statistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchKeyword, setSearchKeyword] = useState('')
  const [searchPlatform, setSearchPlatform] = useState('bilibili')
  const [newKeyword, setNewKeyword] = useState('')
  const [newPlatform, setNewPlatform] = useState('bilibili')
  const [isSearching, setIsSearching] = useState(false)

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 10000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [tasksRes, keywordsRes, statsRes] = await Promise.all([
        axios.get(`${LEARNING_API}/tasks/?limit=20`),
        axios.get(`${LEARNING_API}/keywords/`),
        axios.get(`${LEARNING_API}/statistics/summary`)
      ])
      setTasks(tasksRes.data)
      setKeywords(keywordsRes.data)
      setStats(statsRes.data)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async () => {
    if (!searchKeyword.trim()) return
    
    setIsSearching(true)
    try {
      await axios.post(`${LEARNING_API}/search/`, null, {
        params: {
          platform: searchPlatform,
          keyword: searchKeyword,
          max_results: 5
        }
      })
      setTimeout(loadData, 2000)
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setIsSearching(false)
    }
  }

  const handleAddKeyword = async () => {
    if (!newKeyword.trim()) return
    
    try {
      await axios.post(`${LEARNING_API}/keywords/`, {
        platform: newPlatform,
        keyword: newKeyword
      })
      setNewKeyword('')
      loadData()
    } catch (error) {
      console.error('Add keyword failed:', error)
    }
  }

  const handleDeleteKeyword = async (id: number) => {
    try {
      await axios.delete(`${LEARNING_API}/keywords/${id}`)
      loadData()
    } catch (error) {
      console.error('Delete keyword failed:', error)
    }
  }

  const handleTriggerScheduled = async () => {
    try {
      await axios.post(`${LEARNING_API}/trigger-scheduled/`)
      setTimeout(loadData, 2000)
    } catch (error) {
      console.error('Trigger failed:', error)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="text-green-500" size={18} />
      case 'failed':
        return <XCircle className="text-red-500" size={18} />
      case 'pending':
        return <Clock className="text-yellow-500" size={18} />
      default:
        return <Loader2 className="text-blue-500 animate-spin" size={18} />
    }
  }

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      pending: '等待中',
      downloading: '下载中',
      transcribing: '转写中',
      transcribing_audio: '音频转写中',
      extracting_knowledge: '提取知识中',
      completed: '已完成',
      failed: '失败'
    }
    return statusMap[status] || status
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="animate-spin text-primary-600" size={32} />
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Brain className="text-primary-600" size={24} />
            <h2 className="text-xl font-semibold text-gray-900">自我进化学习</h2>
          </div>
          <button
            onClick={handleTriggerScheduled}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Play size={18} />
            <span>启动学习</span>
          </button>
        </div>

        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              <p className="text-sm text-gray-500">总任务</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
              <p className="text-sm text-gray-500">已完成</p>
            </div>
            <div className="bg-red-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-red-600">{stats.failed}</p>
              <p className="text-sm text-gray-500">失败</p>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
              <p className="text-sm text-gray-500">等待中</p>
            </div>
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-blue-600">{(stats.success_rate * 100).toFixed(1)}%</p>
              <p className="text-sm text-gray-500">成功率</p>
            </div>
          </div>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">搜索视频</h3>
          
          <div className="space-y-4">
            <div className="flex gap-2">
              <select
                value={searchPlatform}
                onChange={(e) => setSearchPlatform(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="bilibili">B站</option>
              </select>
              <input
                type="text"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                placeholder="输入搜索关键词..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
              <button
                onClick={handleSearch}
                disabled={isSearching}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                {isSearching ? <Loader2 className="animate-spin" size={20} /> : <Search size={20} />}
              </button>
            </div>
          </div>

          <div className="mt-6">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium text-gray-700">关键词列表</h4>
              <div className="flex gap-2">
                <select
                  value={newPlatform}
                  onChange={(e) => setNewPlatform(e.target.value)}
                  className="px-2 py-1 text-sm border border-gray-300 rounded"
                >
                  <option value="bilibili">B站</option>
                </select>
                <input
                  type="text"
                  value={newKeyword}
                  onChange={(e) => setNewKeyword(e.target.value)}
                  placeholder="新关键词"
                  className="px-2 py-1 text-sm border border-gray-300 rounded w-24"
                />
                <button
                  onClick={handleAddKeyword}
                  className="p-1 bg-green-500 text-white rounded hover:bg-green-600"
                >
                  <Plus size={16} />
                </button>
              </div>
            </div>
            
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {keywords.map((kw) => (
                <div
                  key={kw.id}
                  className="flex items-center justify-between p-2 bg-gray-50 rounded"
                >
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 bg-primary-100 text-primary-700 text-xs rounded">
                      {kw.platform}
                    </span>
                    <span className="text-sm">{kw.keyword}</span>
                  </div>
                  <button
                    onClick={() => handleDeleteKeyword(kw.id)}
                    className="p-1 text-gray-400 hover:text-red-500"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">学习任务</h3>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {tasks.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Video className="mx-auto mb-2 text-gray-300" size={40} />
                <p>暂无学习任务</p>
                <p className="text-sm">点击"启动学习"开始自动学习</p>
              </div>
            ) : (
              tasks.map((task) => (
                <div
                  key={task.id}
                  className="border border-gray-200 rounded-lg p-3 hover:border-gray-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(task.status)}
                        <span className="text-sm font-medium text-gray-900 truncate">
                          {task.video_title || `任务 #${task.id}`}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                        <span className="px-1.5 py-0.5 bg-gray-100 rounded">
                          {task.platform}
                        </span>
                        <span>{task.keyword}</span>
                        {task.video_author && (
                          <span>· {task.video_author}</span>
                        )}
                      </div>
                      {task.error_message && (
                        <p className="text-xs text-red-500 mt-1 truncate">
                          {task.error_message}
                        </p>
                      )}
                    </div>
                    <div className="text-right">
                      <span className={`text-xs px-2 py-1 rounded ${
                        task.status === 'completed' ? 'bg-green-100 text-green-700' :
                        task.status === 'failed' ? 'bg-red-100 text-red-700' :
                        'bg-blue-100 text-blue-700'
                      }`}>
                        {getStatusText(task.status)}
                      </span>
                      {task.knowledge_extracted && (
                        <div className="flex items-center gap-1 mt-1 text-xs text-green-600">
                          <BookOpen size={12} />
                          <span>已提取知识</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="bg-amber-50 rounded-xl p-4">
        <h4 className="font-medium text-amber-800 mb-2">使用说明</h4>
        <ul className="text-sm text-amber-700 space-y-1">
          <li>• 点击"启动学习"会自动根据关键词搜索视频并提取知识</li>
          <li>• 系统每天凌晨2点自动执行学习任务</li>
          <li>• 提取的知识会自动存入知识库，用于对话分析</li>
          <li>• 可以手动添加关键词来扩展学习范围</li>
        </ul>
      </div>
    </div>
  )
}
