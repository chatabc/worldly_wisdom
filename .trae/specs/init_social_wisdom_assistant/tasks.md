# Tasks

## Phase 1: 项目初始化与Docker环境

- [x] Task 1: 创建项目结构和Docker配置
  - [x] SubTask 1.1: 创建项目目录结构（frontend/backend/learning/ai-service）
  - [x] SubTask 1.2: 编写docker-compose.yml（定义所有服务）
  - [x] SubTask 1.3: 编写各服务的Dockerfile
  - [x] SubTask 1.4: 创建.env.example环境变量模板
  - [x] SubTask 1.5: 编写启动脚本和说明文档

- [x] Task 2: 搭建数据层服务
  - [x] SubTask 2.1: 配置PostgreSQL数据库
  - [x] SubTask 2.2: 配置ChromaDB向量数据库
  - [x] SubTask 2.3: 配置Redis缓存和任务队列
  - [x] SubTask 2.4: 配置MinIO文件存储
  - [x] SubTask 2.5: 创建数据库初始化脚本

## Phase 2: 后端API服务

- [x] Task 3: 搭建FastAPI后端框架
  - [x] SubTask 3.1: 创建FastAPI项目结构
  - [x] SubTask 3.2: 配置CORS、日志、异常处理
  - [x] SubTask 3.3: 实现健康检查和基础API
  - [x] SubTask 3.4: 配置数据库连接（SQLAlchemy）

- [x] Task 4: 实现AI模型接入层
  - [x] SubTask 4.1: 创建模型配置管理（API Key、模型选择）
  - [x] SubTask 4.2: 实现OpenAI API调用封装
  - [x] SubTask 4.3: 实现通义千问API调用封装
  - [x] SubTask 4.4: 实现Ollama本地模型调用封装
  - [x] SubTask 4.5: 创建统一的模型调用接口（支持切换）

- [x] Task 5: 实现对话分析核心逻辑
  - [x] SubTask 5.1: 设计分析Prompt模板（意图识别、隐喻分析、情绪判断）
  - [x] SubTask 5.2: 设计回复建议Prompt模板
  - [x] SubTask 5.3: 实现分析API接口
  - [x] SubTask 5.4: 实现分析结果解析和格式化

- [x] Task 6: 实现知识库模块
  - [x] SubTask 6.1: 设计知识条目数据模型
  - [x] SubTask 6.2: 实现知识库CRUD接口
  - [x] SubTask 6.3: 实现向量嵌入和存储
  - [x] SubTask 6.4: 实现RAG检索增强生成
  - [x] SubTask 6.5: 导入初始知识库数据（经典社交技巧内容）

## Phase 3: 前端界面

- [x] Task 7: 搭建React前端项目
  - [x] SubTask 7.1: 使用Vite创建React + TypeScript项目
  - [x] SubTask 7.2: 配置TailwindCSS和Shadcn/ui
  - [x] SubTask 7.3: 配置路由和状态管理（Zustand）
  - [x] SubTask 7.4: 创建基础布局组件

- [x] Task 8: 实现核心UI组件
  - [x] SubTask 8.1: 创建对话输入区域（文本输入框）
  - [x] SubTask 8.2: 创建分析结果展示区域
  - [x] SubTask 8.3: 创建回复建议卡片组件
  - [x] SubTask 8.4: 创建模型配置设置页面
  - [x] SubTask 8.5: 创建知识库管理页面

- [x] Task 9: 实现截屏功能
  - [x] SubTask 9.1: 实现截图上传组件
  - [x] SubTask 9.2: 实现截图预览功能
  - [x] SubTask 9.3: 调用后端多模态分析API
  - [x] SubTask 9.4: 展示图片分析结果

## Phase 4: 自我进化学习系统（第二阶段）

- [x] Task 10: 搭建学习服务框架
  - [x] SubTask 10.1: 创建Celery任务队列配置
  - [x] SubTask 10.2: 实现任务调度器（定时任务）
  - [x] SubTask 10.3: 创建学习任务管理API

- [x] Task 11: 实现视频抓取模块
  - [x] SubTask 11.1: 集成TikTokDownloader核心功能
  - [x] SubTask 11.2: 实现抖音视频搜索和下载
  - [x] SubTask 11.3: 实现B站视频下载（参考BiliNote）
  - [x] SubTask 11.4: 实现关键词配置管理
  - [x] SubTask 11.5: 实现下载队列和进度追踪

- [x] Task 12: 实现视频内容提取模块
  - [x] SubTask 12.1: 集成Whisper语音转写
  - [x] SubTask 12.2: 实现视频字幕提取
  - [x] SubTask 12.3: 实现关键帧提取（参考Video-Analyzer）
  - [x] SubTask 12.4: 实现多模态内容分析

- [x] Task 13: 实现知识提取和入库
  - [x] SubTask 13.1: 设计知识点提取Prompt
  - [x] SubTask 13.2: 实现AI知识点提取逻辑
  - [x] SubTask 13.3: 实现知识点结构化存储
  - [x] SubTask 13.4: 实现学习进度追踪API
  - [x] SubTask 13.5: 创建学习记录展示页面

## Phase 5: 音频功能（第三阶段）

- [x] Task 14: 实现音频处理模块
  - [x] SubTask 14.1: 实现音频文件上传接口
  - [x] SubTask 14.2: 集成Whisper音频转写
  - [x] SubTask 14.3: 实现实时语音捕获（WebSocket）
  - [x] SubTask 14.4: 实现转写结果流式返回

## Phase 6: 测试与优化

- [ ] Task 15: 测试与文档
  - [ ] SubTask 15.1: 编写后端单元测试
  - [ ] SubTask 15.2: 编写集成测试
  - [ ] SubTask 15.3: 性能优化
  - [ ] SubTask 15.4: 编写用户使用文档

# Task Dependencies
- Task 2 依赖 Task 1
- Task 3 依赖 Task 1, Task 2
- Task 4 依赖 Task 3
- Task 5 依赖 Task 4
- Task 6 依赖 Task 3, Task 4
- Task 7 依赖 Task 1
- Task 8 依赖 Task 7
- Task 9 依赖 Task 8, Task 5
- Task 10 依赖 Task 2, Task 3
- Task 11 依赖 Task 10
- Task 12 依赖 Task 11
- Task 13 依赖 Task 12, Task 6
- Task 14 依赖 Task 3, Task 4

# MVP优先级
**第一阶段（MVP - 桌面端核心功能）**: Task 1, 2, 3, 4, 5, 6, 7, 8, 9 ✅ 已完成
**第二阶段（自我进化学习）**: Task 10, 11, 12, 13 ✅ 已完成
**第三阶段（音频功能）**: Task 14 ✅ 已完成
**收尾阶段**: Task 15
