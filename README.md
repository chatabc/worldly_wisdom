# 人情世故助手 (Social Wisdom Assistant)

> AI驱动的社交智慧助手，帮助理解他人言语背后的真实意图，并提供恰当的回复建议。

## 功能特性

### 核心功能
- 🧠 **对话意图分析**：深度解析言语背后的真实意图、隐喻和潜台词
- 💬 **回复建议生成**：提供多种回复方案，包含利弊分析
- 📸 **截屏分析**：支持上传截图进行多模态分析
- 📚 **知识库**：丰富的社交技巧知识，支持RAG检索增强
- 🔧 **多模型支持**：OpenAI、通义千问、Ollama本地模型

### 技术架构
- 🐳 **Docker容器化**：一键部署，环境隔离
- ⚡ **FastAPI后端**：高性能异步API
- ⚛️ **React前端**：现代化用户界面
- 🗄️ **PostgreSQL**：结构化数据存储
- 🔍 **ChromaDB**：向量知识库
- 📦 **Redis**：缓存和任务队列
- 📁 **MinIO**：文件存储

### 未来规划
- 🎬 **自我进化学习**：自动从抖音/B站抓取视频并提取知识
- 🎤 **实时语音分析**：支持实时语音转写和分析
- 📱 **手机端**：独立手机应用，实时监听和分析

## 快速开始

### 前置要求
- Docker 和 Docker Compose
- 至少 4GB 可用内存
- 10GB 可用磁盘空间

### 一键启动

1. 克隆项目
```bash
git clone <repository-url>
cd worldly_wisdom
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Keys
```

3. 启动所有服务
```bash
docker-compose up -d
```

4. 访问应用
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- MinIO控制台: http://localhost:9001 (minioadmin/minioadmin123)

### 停止服务
```bash
docker-compose down
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 配置说明

### API Keys配置

在 `.env` 文件中配置以下API Keys：

```env
# OpenAI API (推荐用于多模态分析)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o

# 通义千问 API (中文理解能力强)
QWEN_API_KEY=your-qwen-api-key
QWEN_MODEL=qwen-max

# 文心一言 API
WENXIN_API_KEY=your-wenxin-api-key
WENXIN_SECRET_KEY=your-wenxin-secret-key
```

### 本地模型 (Ollama)

如果使用本地Ollama模型，需要：

1. 安装Ollama
```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# 下载安装包: https://ollama.ai/download
```

2. 下载模型
```bash
ollama pull qwen2.5:7b
ollama pull llava
```

3. 在设置页面切换到Ollama模型

## 项目结构

```
worldly_wisdom/
├── frontend/           # React前端应用
│   ├── src/
│   │   ├── components/  # UI组件
│   │   ├── pages/       # 页面
│   │   ├── stores/      # Zustand状态管理
│   │   ├── services/    # API服务
│   │   └── types/      # TypeScript类型
│   ├── package.json
│   └── Dockerfile
├── backend/            # FastAPI后端
│   ├── app/
│   │   ├── routers/     # API路由
│   │   ├── models/      # 数据模型
│   │   ├── services/    # 业务逻辑
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── learning/           # 学习服务（第二阶段）
├── docker-compose.yml   # Docker编排
├── .env.example       # 环境变量模板
└── README.md
```

## 开发指南

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

### 后端开发
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 数据库初始化
```bash
# 连接到PostgreSQL容器
docker exec -it worldly_wisdom-db-1 psql -U wisdom -d wisdom_db

# 执行初始化脚本
psql -U wisdom -d wisdom_db -f init-db.sql
```

## API文档

启动服务后，访问 http://localhost:8000/docs 查看完整的API文档。

主要API端点：
- `POST /api/analysis/analyze` - 对话分析
- `GET /api/knowledge/` - 知识库列表
- `POST /api/knowledge/` - 添加知识
- `GET /api/config/` - 模型配置
- `POST /api/config/{provider}/activate` - 切换模型

## 常见问题

### Q: Docker启动失败？
A: 检查端口是否被占用，确保3000、8000、5432、6379、9000、9001、11434端口可用。

### Q: API调用失败？
A: 检查 `.env` 文件中的API Keys是否正确配置，确保网络可以访问对应的API服务。

### Q: Ollama模型无法使用？
A: 确保Ollama服务正常运行，并且已下载相应的模型。使用 `ollama list` 查看已安装的模型。

### Q: 如何添加自定义知识？
A: 访问知识库页面，可以手动添加知识条目。第二阶段将支持自动从视频学习。

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 致谢

感谢以下开源项目：
- [TikTokDownloader](https://github.com/JoeanAmier/TikTokDownloader) - 视频下载
- [Video-Analyzer](https://github.com/LLM-Red-Team/Video-Analyzer) - 视频分析
- [ChromaDB](https://github.com/chroma-core/chroma) - 向量数据库
- [Ollama](https://github.com/ollama/ollama) - 本地模型运行
- [FastAPI](https://github.com/tiangolo/fastapi) - Python Web框架
- [React](https://github.com/facebook/react) - 前端框架

## 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [GitHub Issues]

---

**注意**：本项目仅供学习和研究使用，请勿用于非法用途。使用本应用分析他人对话时，请遵守相关法律法规和隐私保护原则。
