import React, { useState, useEffect } from 'react'
import { Settings as SettingsIcon, Check, Loader2 } from 'lucide-react'
import { getModelConfigs, activateModel } from '@/services/api'
import { ModelConfig } from '@/types'

export default function Settings() {
  const [configs, setConfigs] = useState<ModelConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [activating, setActivating] = useState<string | null>(null)

  useEffect(() => {
    loadConfigs()
  }, [])

  const loadConfigs = async () => {
    try {
      const data = await getModelConfigs()
      setConfigs(data)
    } catch (error) {
      console.error('Failed to load configs:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleActivate = async (provider: string) => {
    setActivating(provider)
    try {
      await activateModel(provider)
      await loadConfigs()
    } catch (error) {
      console.error('Failed to activate model:', error)
    } finally {
      setActivating(null)
    }
  }

  const providerInfo: Record<string, { name: string; description: string }> = {
    openai: {
      name: 'OpenAI',
      description: 'GPT-4o 多模态模型，支持文本和图片分析'
    },
    qwen: {
      name: '通义千问',
      description: '阿里云大模型，中文理解能力强'
    },
    ollama: {
      name: 'Ollama (本地)',
      description: '本地部署模型，隐私安全，需要本地运行Ollama'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="animate-spin text-primary-600" size={32} />
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-6">
          <SettingsIcon className="text-gray-600" size={24} />
          <h2 className="text-xl font-semibold text-gray-900">模型设置</h2>
        </div>

        <div className="space-y-4">
          {configs.map((config) => {
            const info = providerInfo[config.provider] || {
              name: config.provider,
              description: config.model_name
            }
            
            return (
              <div
                key={config.provider}
                className={`
                  border rounded-lg p-4 transition-colors
                  ${config.is_active 
                    ? 'border-primary-500 bg-primary-50' 
                    : 'border-gray-200 hover:border-gray-300'}
                `}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium text-gray-900">{info.name}</h3>
                      {config.is_active && (
                        <span className="px-2 py-0.5 bg-primary-600 text-white text-xs rounded-full">
                          当前使用
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500 mt-1">{info.description}</p>
                    <p className="text-xs text-gray-400 mt-1">模型: {config.model_name}</p>
                  </div>
                  
                  {!config.is_active && (
                    <button
                      onClick={() => handleActivate(config.provider)}
                      disabled={activating !== null}
                      className={`
                        flex items-center gap-2 px-4 py-2 rounded-lg transition-colors
                        ${activating === config.provider
                          ? 'bg-gray-100 text-gray-400'
                          : 'bg-primary-600 text-white hover:bg-primary-700'}
                      `}
                    >
                      {activating === config.provider ? (
                        <>
                          <Loader2 className="animate-spin" size={16} />
                          <span>切换中</span>
                        </>
                      ) : (
                        <>
                          <Check size={16} />
                          <span>启用</span>
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        <div className="mt-6 p-4 bg-amber-50 rounded-lg">
          <h4 className="font-medium text-amber-800 mb-2">配置说明</h4>
          <ul className="text-sm text-amber-700 space-y-1">
            <li>• OpenAI 需要在环境变量中设置 OPENAI_API_KEY</li>
            <li>• 通义千问需要在环境变量中设置 QWEN_API_KEY</li>
            <li>• Ollama 需要本地运行 Ollama 服务并下载相应模型</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
