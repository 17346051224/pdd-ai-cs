# 拼多多AI售前客服系统

基于 DeepSeek 大模型的智能客服系统，支持知识库管理、对话记录查看、数据统计等功能。

## 功能特性

- 🤖 **AI智能回复** - 基于DeepSeek大模型的自然语言处理
- 📚 **知识库管理** - 支持商品FAQ、常见问题等知识库CRUD
- ⚙️ **客服配置** - 可自定义AI人设、回复风格、Prompt模板
- 💬 **对话记录** - 完整的对话历史查看和导出
- 📊 **数据统计** - 对话数、回复率、满意度等多维度统计
- 🛒 **拼多多对接** - 预留接口（需备案后配置）

## 技术栈

- **后端**: Python 3.11 + FastAPI + SQLAlchemy + SQLite
- **前端**: Vue 3 + Vite + Element Plus + ECharts
- **部署**: Docker + Docker Compose + Nginx

## 快速开始

### 1. 环境要求

- Docker 20.10+
- Docker Compose 2.0+

### 2. 配置

创建 `.env` 文件（可选）:

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
DEBUG=false
```

### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 访问系统

- 前端地址: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

默认登录账号: `admin` / `admin123`

## 项目结构

```
pdd-ai-cs/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── main.py        # FastAPI入口
│   │   ├── config.py      # 配置管理
│   │   ├── models.py      # 数据库模型
│   │   ├── schemas.py     # Pydantic模型
│   │   ├── database.py    # 数据库连接
│   │   ├── routers/       # API路由
│   │   └── services/      # 业务服务
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # 前端服务
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── router/       # 路由配置
│   │   ├── store/        # 状态管理
│   │   └── assets/       # 静态资源
│   ├── package.json
│   └── Dockerfile
├── nginx/
│   └── nginx.conf        # Nginx配置
├── docker-compose.yml
└── README.md
```

## API接口

### 对话
- `POST /api/chat/chat` - 发送消息获取AI回复
- `GET /api/chat/history/{session_id}` - 获取会话历史
- `GET /api/chat/sessions` - 获取所有会话列表
- `POST /api/chat/rate/{message_id}` - 评价对话

### 知识库
- `GET /api/knowledge` - 获取知识库列表
- `POST /api/knowledge` - 创建知识条目
- `PUT /api/knowledge/{id}` - 更新知识条目
- `DELETE /api/knowledge/{id}` - 删除知识条目
- `POST /api/knowledge/import` - 批量导入

### 配置
- `GET /api/config/ai` - 获取AI配置
- `PUT /api/config/ai` - 更新AI配置
- `GET /api/config/ai/test` - 测试API连接

### 统计
- `GET /api/stats/overall` - 总体统计
- `GET /api/stats/daily` - 每日统计
- `GET /api/stats/chart` - 图表数据

## 部署到阿里云

### 方式一：直接部署

```bash
# 1. 上传代码到服务器
scp -r ./pdd-ai-cs root@116.62.129.232:/opt/

# 2. SSH登录服务器
ssh root@116.62.129.232

# 3. 进入项目目录
cd /opt/pdd-ai-cs

# 4. 启动服务
docker-compose up -d --build
```

### 方式二：使用部署脚本

```bash
# 在服务器上执行
curl -sSL https://raw.githubusercontent.com/your-repo/deploy.sh | sh
```

## 访问地址

- **IP访问**: http://116.62.129.232:3000
- **API地址**: http://116.62.129.232:8000

> 注意：域名 `kekewang.top` 备案中，备案完成后可配置域名访问。

## 注意事项

1. **API Key安全**: 生产环境请勿将API Key提交到代码仓库，使用环境变量或密钥管理服务
2. **备案要求**: 拼多多开放平台API对接需要完成ICP备案
3. **数据备份**: 定期备份 `./backend/data/pdd_cs.db` 数据库文件

## 许可证

MIT License
