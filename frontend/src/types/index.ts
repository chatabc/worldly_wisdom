export interface IntentAnalysis {
  real_intent: string
  metaphors: string[]
  emotional_state: string
  attitude: string
  potential_traps: string[]
}

export interface ReplySuggestion {
  type: string
  content: string
  pros: string[]
  cons: string[]
}

export interface AnalysisResult {
  intent_analysis: IntentAnalysis
  reply_suggestions: ReplySuggestion[]
  related_knowledge: string[]
  model_used: string
}

export interface KnowledgeItem {
  id: number
  title: string
  content: string
  category: string | null
  tags: string[] | null
  source: string | null
  source_url: string | null
  created_at: string
}

export interface ModelConfig {
  id: number
  provider: string
  model_name: string
  is_active: boolean
  created_at: string
}
