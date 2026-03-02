import React, { useState, useEffect } from 'react'
import { BookOpen, Plus, Trash2, Search, Loader2 } from 'lucide-react'
import { getKnowledgeItems, getCategories, deleteKnowledgeItem } from '@/services/api'
import { KnowledgeItem } from '@/types'

export default function Knowledge() {
  const [items, setItems] = useState<KnowledgeItem[]>([])
  const [categories, setCategories] = useState<{ name: string; count: number }[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [selectedCategory, search])

  const loadData = async () => {
    setLoading(true)
    try {
      const [itemsData, categoriesData] = await Promise.all([
        getKnowledgeItems(0, 50, selectedCategory || undefined, search || undefined),
        getCategories()
      ])
      setItems(itemsData)
      setCategories(categoriesData)
    } catch (error) {
      console.error('Failed to load knowledge:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这条知识吗？')) return
    
    try {
      await deleteKnowledgeItem(id)
      loadData()
    } catch (error) {
      console.error('Failed to delete:', error)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <BookOpen className="text-gray-600" size={24} />
            <h2 className="text-xl font-semibold text-gray-900">知识库</h2>
          </div>
          
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="搜索知识..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>

        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`
              px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors
              ${!selectedCategory 
                ? 'bg-primary-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}
            `}
          >
            全部
          </button>
          {categories.map((cat) => (
            <button
              key={cat.name}
              onClick={() => setSelectedCategory(cat.name)}
              className={`
                px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors
                ${selectedCategory === cat.name 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}
              `}
            >
              {cat.name} ({cat.count})
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-32">
            <Loader2 className="animate-spin text-primary-600" size={32} />
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <BookOpen className="mx-auto mb-4 text-gray-300" size={48} />
            <p>暂无知识内容</p>
            <p className="text-sm mt-1">可以通过学习服务自动获取或手动添加</p>
          </div>
        ) : (
          <div className="space-y-4">
            {items.map((item) => (
              <div
                key={item.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{item.title}</h3>
                    <p className="text-sm text-gray-600 mt-1 line-clamp-2">{item.content}</p>
                    <div className="flex items-center gap-2 mt-2">
                      {item.category && (
                        <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                          {item.category}
                        </span>
                      )}
                      {item.tags?.map((tag) => (
                        <span
                          key={tag}
                          className="px-2 py-0.5 bg-primary-50 text-primary-600 text-xs rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                    {item.source && (
                      <p className="text-xs text-gray-400 mt-2">来源: {item.source}</p>
                    )}
                  </div>
                  <button
                    onClick={() => handleDelete(item.id)}
                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
