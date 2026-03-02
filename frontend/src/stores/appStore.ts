import { create } from 'zustand'
import { IntentAnalysis, ReplySuggestion } from '@/types'

interface AppState {
  isLoading: boolean
  error: string | null
  inputText: string
  imageBase64: string | null
  analysisResult: {
    intentAnalysis: IntentAnalysis | null
    replySuggestions: ReplySuggestion[]
    relatedKnowledge: string[]
    modelUsed: string
  } | null
  modelProvider: string
  
  setInputText: (text: string) => void
  setImageBase64: (image: string | null) => void
  setAnalysisResult: (result: AppState['analysisResult']) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setModelProvider: (provider: string) => void
  clearAnalysis: () => void
}

export const useAppStore = create<AppState>((set) => ({
  isLoading: false,
  error: null,
  inputText: '',
  imageBase64: null,
  analysisResult: null,
  modelProvider: 'openai',

  setInputText: (text) => set({ inputText: text }),
  setImageBase64: (image) => set({ imageBase64: image }),
  setAnalysisResult: (result) => set({ analysisResult: result, isLoading: false, error: null }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error, isLoading: false }),
  setModelProvider: (provider) => set({ modelProvider: provider }),
  clearAnalysis: () => set({ 
    analysisResult: null, 
    inputText: '', 
    imageBase64: null, 
    error: null 
  }),
}))
