import React, { useState, useRef } from 'react'
import { 
  Send, 
  Image, 
  Loader2, 
  AlertCircle,
  Lightbulb,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  Trash2,
  Copy,
  Check
} from 'lucide-react'
import { useAppStore } from '@/stores/appStore'
import { analyzeConversation } from '@/services/api'

export default function Home() {
  const {
    inputText,
    setInputText,
    imageBase64,
    setImageBase64,
    analysisResult,
    setAnalysisResult,
    isLoading,
    setLoading,
    error,
    setError,
    clearAnalysis
  } = useAppStore()
  
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        const base64 = reader.result as string
        setImageBase64(base64.split(',')[1])
      }
      reader.readAsDataURL(file)
    }
  }

  const handleAnalyze = async () => {
    if (!inputText.trim() && !imageBase64) {
      setError('请输入对话内容或上传图片')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const result = await analyzeConversation(
        inputText.trim() || undefined,
        imageBase64 || undefined
      )
      setAnalysisResult({
        intentAnalysis: result.intent_analysis,
        replySuggestions: result.reply_suggestions,
        relatedKnowledge: result.related_knowledge,
        modelUsed: result.model_used
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || '分析失败，请重试')
    }
  }

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">对话分析</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              输入对话内容
            </label>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="粘贴或输入你想分析的对话内容..."
              className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              或上传截图
            </label>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Image size={20} />
              <span>选择图片</span>
            </button>
            
            {imageBase64 && (
              <div className="mt-3 relative inline-block">
                <img
                  src={`data:image/jpeg;base64,${imageBase64}`}
                  alt="上传的图片"
                  className="max-h-40 rounded-lg border border-gray-200"
                />
                <button
                  onClick={() => setImageBase64(null)}
                  className="absolute -top-2 -right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            )}
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 text-red-700 rounded-lg">
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={handleAnalyze}
              disabled={isLoading}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  <span>分析中...</span>
                </>
              ) : (
                <>
                  <Send size={20} />
                  <span>开始分析</span>
                </>
              )}
            </button>
            
            {(inputText || imageBase64) && (
              <button
                onClick={clearAnalysis}
                className="px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                清空
              </button>
            )}
          </div>
        </div>
      </div>

      {analysisResult && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb className="text-amber-500" size={24} />
              <h3 className="text-lg font-semibold text-gray-900">意图分析</h3>
            </div>
            
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-700 mb-1">真实意图</h4>
                <p className="text-gray-900 bg-gray-50 p-3 rounded-lg">
                  {analysisResult.intentAnalysis?.real_intent}
                </p>
              </div>
              
              {analysisResult.intentAnalysis?.metaphors?.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-1">隐喻和暗示</h4>
                  <ul className="list-disc list-inside text-gray-900 bg-gray-50 p-3 rounded-lg">
                    {analysisResult.intentAnalysis.metaphors.map((m, i) => (
                      <li key={i}>{m}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-gray-700 mb-1">情绪状态</h4>
                  <p className="text-gray-900 bg-gray-50 p-3 rounded-lg">
                    {analysisResult.intentAnalysis?.emotional_state}
                  </p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-700 mb-1">态度分析</h4>
                  <p className="text-gray-900 bg-gray-50 p-3 rounded-lg">
                    {analysisResult.intentAnalysis?.attitude}
                  </p>
                </div>
              </div>
              
              {analysisResult.intentAnalysis?.potential_traps?.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-1">潜在陷阱</h4>
                  <ul className="list-disc list-inside text-red-700 bg-red-50 p-3 rounded-lg">
                    {analysisResult.intentAnalysis.potential_traps.map((t, i) => (
                      <li key={i}>{t}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <MessageSquare className="text-primary-600" size={24} />
              <h3 className="text-lg font-semibold text-gray-900">回复建议</h3>
            </div>
            
            <div className="space-y-4">
              {analysisResult.replySuggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="border border-gray-200 rounded-lg p-4 hover:border-primary-300 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="px-2 py-1 bg-primary-100 text-primary-700 text-sm font-medium rounded">
                      {suggestion.type}
                    </span>
                    <button
                      onClick={() => handleCopy(suggestion.content, index)}
                      className="p-1 hover:bg-gray-100 rounded"
                    >
                      {copiedIndex === index ? (
                        <Check size={18} className="text-green-600" />
                      ) : (
                        <Copy size={18} className="text-gray-500" />
                      )}
                    </button>
                  </div>
                  
                  <p className="text-gray-900 mb-3">{suggestion.content}</p>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="flex items-center gap-1 text-green-600 mb-1">
                        <ThumbsUp size={14} />
                        <span>优点</span>
                      </div>
                      <ul className="text-gray-600 space-y-1">
                        {suggestion.pros.map((pro, i) => (
                          <li key={i}>• {pro}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <div className="flex items-center gap-1 text-red-500 mb-1">
                        <ThumbsDown size={14} />
                        <span>风险</span>
                      </div>
                      <ul className="text-gray-600 space-y-1">
                        {suggestion.cons.map((con, i) => (
                          <li key={i}>• {con}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-4 text-sm text-gray-500 text-right">
              使用模型: {analysisResult.modelUsed}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
