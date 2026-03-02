import React, { useState, useRef, useEffect } from 'react'
import { 
  Mic, 
  MicOff, 
  Square, 
  Upload, 
  Loader2, 
  Play,
  Pause,
  Copy,
  Check,
  AlertCircle,
  FileAudio
} from 'lucide-react'
import { useAppStore } from '@/stores/appStore'
import { analyzeConversation } from '@/services/api'

const API_URL = 'http://localhost:8000'

export default function Audio() {
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [transcription, setTranscription] = useState<string>('')
  const [segments, setSegments] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  
  const { setAnalysisResult, setLoading, setError: setAppError } = useAppStore()

  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObject(audioUrl)
      }
    }
  }, [audioUrl])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setAudioBlob(blob)
        setAudioUrl(URL.createObjectURL(blob))
        stream.getTracks().forEach(track => track.stop())
      }
      
      mediaRecorder.start(1000)
      setIsRecording(true)
      setError(null)
    } catch (err: any) {
      setError('无法访问麦克风: ' + err.message)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setAudioBlob(file)
      setAudioUrl(URL.createObjectURL(file))
      setError(null)
    }
  }

  const uploadAndTranscribe = async () => {
    if (!audioBlob) {
      setError('请先录制或上传音频')
      return
    }

    setIsUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', audioBlob, 'audio.webm')

      const response = await fetch(`${API_URL}/api/audio/analyze`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error('上传失败')
      }

      const result = await response.json()
      
      setTranscription(result.transcription)
      setSegments(result.segments || [])
      
      if (result.analysis) {
        try {
          const analysisData = typeof result.analysis === 'string' 
            ? JSON.parse(result.analysis) 
            : result.analysis
          
          setAnalysisResult({
            intentAnalysis: analysisData.intent_analysis || {
              real_intent: analysisData.real_intent || '',
              metaphors: analysisData.metaphors || [],
              emotional_state: analysisData.emotional_state || '',
              attitude: analysisData.attitude || '',
              potential_traps: analysisData.potential_traps || []
            },
            replySuggestions: analysisData.reply_suggestions || [],
            relatedKnowledge: analysisData.related_knowledge || [],
            modelUsed: 'whisper'
          })
        } catch {
          setTranscription(result.transcription + '\n\n分析结果解析失败')
        }
      }
    } catch (err: any) {
      setError('处理失败: ' + err.message)
    } finally {
      setIsUploading(false)
    }
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(transcription)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const togglePlayback = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        audioRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">音频分析</h2>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-gray-300 rounded-xl">
              {isRecording ? (
                <div className="text-center">
                  <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
                    <MicOff className="text-white" size={32} />
                  </div>
                  <p className="text-red-600 font-medium">正在录音...</p>
                  <button
                    onClick={stopRecording}
                    className="mt-4 px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                  >
                    停止录音
                  </button>
                </div>
              ) : (
                <div className="text-center">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Mic className="text-gray-400" size={32} />
                  </div>
                  <p className="text-gray-500 mb-4">点击开始录音</p>
                  <button
                    onClick={startRecording}
                    className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    <Mic size={18} className="inline mr-2" />
                    开始录音
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-gray-300 rounded-xl">
              <input
                ref={fileInputRef}
                type="file"
                accept="audio/*"
                onChange={handleFileUpload}
                className="hidden"
              />
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Upload className="text-gray-400" size={32} />
              </div>
              <p className="text-gray-500 mb-4">或上传音频文件</p>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Upload size={18} className="inline mr-2" />
                选择文件
              </button>
            </div>
          </div>
        </div>

        {audioUrl && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-4">
              <button
                onClick={togglePlayback}
                className="p-2 bg-primary-600 text-white rounded-full hover:bg-primary-700"
              >
                {isPlaying ? <Pause size={20} /> : <Play size={20} />}
              </button>
              <audio
                ref={audioRef}
                src={audioUrl}
                onEnded={() => setIsPlaying(false)}
                className="flex-1"
                controls
              />
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 text-red-700 rounded-lg">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        <button
          onClick={uploadAndTranscribe}
          disabled={!audioBlob || isUploading}
          className="w-full mt-4 flex items-center justify-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isUploading ? (
            <>
              <Loader2 className="animate-spin" size={20} />
              <span>处理中...</span>
            </>
          ) : (
            <>
              <FileAudio size={20} />
              <span>转写并分析</span>
            </>
          )}
        </button>
      </div>

      {transcription && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">转写结果</h3>
            <button
              onClick={copyToClipboard}
              className="flex items-center gap-1 px-3 py-1 text-sm text-gray-600 hover:text-gray-900"
            >
              {copied ? (
                <>
                  <Check size={16} className="text-green-600" />
                  <span className="text-green-600">已复制</span>
                </>
              ) : (
                <>
                  <Copy size={16} />
                  <span>复制</span>
                </>
              )}
            </button>
          </div>
          
          <div className="prose max-w-none">
            <p className="whitespace-pre-wrap text-gray-700">{transcription}</p>
          </div>

          {segments.length > 0 && (
            <div className="mt-6">
              <h4 className="text-sm font-medium text-gray-700 mb-3">时间轴</h4>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {segments.map((seg, idx) => (
                  <div key={idx} className="flex gap-3 text-sm">
                    <span className="text-gray-400 font-mono w-20">
                      {Math.floor(seg.start / 60)}:{(seg.start % 60).toFixed(0).padStart(2, '0')}
                    </span>
                    <span className="text-gray-600">{seg.text}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
