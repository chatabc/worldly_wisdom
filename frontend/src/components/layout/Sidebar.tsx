import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  MessageSquare, 
  Settings, 
  BookOpen, 
  Brain,
  Menu,
  X,
  GraduationCap,
  Mic
} from 'lucide-react'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

const navItems = [
  { path: '/', icon: MessageSquare, label: '对话分析' },
  { path: '/audio', icon: Mic, label: '音频分析' },
  { path: '/learning', icon: GraduationCap, label: '自我学习' },
  { path: '/knowledge', icon: BookOpen, label: '知识库' },
  { path: '/settings', icon: Settings, label: '设置' },
]

export default function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const location = useLocation()

  return (
    <>
      <button
        onClick={onToggle}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md"
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-40
          w-64 bg-white border-r border-gray-200
          transform transition-transform duration-200 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <div className="flex flex-col h-full">
          <div className="flex items-center gap-3 p-6 border-b border-gray-200">
            <Brain className="w-8 h-8 text-primary-600" />
            <div>
              <h1 className="text-lg font-bold text-gray-900">人情世故助手</h1>
              <p className="text-xs text-gray-500">Social Wisdom</p>
            </div>
          </div>

          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => window.innerWidth < 1024 && onToggle()}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg
                    transition-colors duration-200
                    ${isActive 
                      ? 'bg-primary-50 text-primary-700 font-medium' 
                      : 'text-gray-600 hover:bg-gray-100'}
                  `}
                >
                  <Icon size={20} />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>

          <div className="p-4 border-t border-gray-200">
            <div className="px-4 py-3 bg-primary-50 rounded-lg">
              <p className="text-sm text-primary-700 font-medium">提示</p>
              <p className="text-xs text-primary-600 mt-1">
                输入对话内容，AI将帮你分析言外之意
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}
