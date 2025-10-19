# Telegram Signal API

一个标准化、模块化的Telegram消息发送API服务。

## 📁 项目结构

```
dexs-tg-signal/
├── main.py                 # 主启动文件
├── requirements.txt        # 项目依赖
├── .env                    # 环境配置
├── .env.example           # 配置模板
│
├── api/                   # API核心模块
│   ├── __init__.py
│   ├── config.py         # 配置管理
│   │
│   ├── core/             # 核心功能
│   │   ├── __init__.py
│   │   └── telegram.py   # Telegram Bot封装
│   │
│   ├── routers/          # API路由
│   │   ├── __init__.py
│   │   ├── health.py     # 健康检查
│   │   └── message.py    # 消息发送
│   │
│   └── utils/            # 工具模块
│       ├── __init__.py
│       └── logger.py     # 日志配置
│
├── tests/                # 测试文件
│   ├── __init__.py
│   └── test_api.py
│
├── tools/                # 辅助工具
│   ├── get_chat_id.py    # 获取群组ID
│   └── test_sender.py    # 测试发送
│
└── docs/                 # 文档
    ├── API.md            # API文档
    └── DEPLOYMENT.md     # 部署指南
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
# BOT_TOKEN=你的Bot Token
# CHAT_ID=你的群组ID
```

### 3. 启动服务

```bash
python main.py
```

服务启动后会显示：
```
🚀 Starting Telegram Signal API
✅ Bot connected: @YourBot
🌐 API Server: http://0.0.0.0:5001
```

## 📡 API端点

### 健康检查
```bash
GET /health
```

### 发送消息
```bash
POST /api/v1/send
Content-Type: application/json

{
  "message": "Hello!",
  "chat_id": -1234567890  // 可选
}
```

### 批量发送
```bash
POST /api/v1/send/multiple
Content-Type: application/json

{
  "message": "Broadcast message",
  "chat_ids": [-1234567890, -9876543210]
}
```

### 发送交易信号
```bash
POST /api/v1/send/formatted
Content-Type: application/json

{
  "chain": "Ethereum",
  "token": "USDT",
  "amount": 10000,
  "action": "Buy"
}
```

## 💻 使用示例

### Python

```python
import requests

# 发送消息
response = requests.post('http://localhost:5001/api/v1/send', json={
    'message': '**Hello!**'
})
print(response.json())
```

### curl

```bash
curl -X POST http://localhost:5001/api/v1/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from API!"}'
```

## 🛠️ 开发

### 运行测试

```bash
python tests/test_api.py
```

### 代码结构说明

- **api/config.py**: 集中管理所有配置
- **api/core/telegram.py**: Telegram Bot核心功能封装
- **api/routers/**: API路由模块化
- **api/utils/**: 通用工具函数
- **main.py**: 应用入口，负责初始化和启动

### 添加新路由

1. 在 `api/routers/` 创建新的路由文件
2. 定义Blueprint和路由
3. 在 `main.py` 中注册Blueprint

示例:
```python
# api/routers/new_feature.py
from flask import Blueprint

new_bp = Blueprint('new_feature', __name__, url_prefix='/api/v1')

@new_bp.route('/new-endpoint', methods=['POST'])
def new_endpoint():
    return {'status': 'ok'}
```

## 📦 部署

### 开发环境
```bash
python main.py
```

### 生产环境 (使用gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 'main:create_app()'
```

### Docker
```bash
docker build -t telegram-api .
docker run -p 5001:5001 --env-file .env telegram-api
```

## 📝 环境变量

| 变量 | 说明 | 默认值 | 必需 |
|------|------|--------|------|
| BOT_TOKEN | Telegram Bot Token | - | ✅ |
| CHAT_ID | 默认群组ID | - | ❌ |
| API_HOST | API监听地址 | 0.0.0.0 | ❌ |
| API_PORT | API端口 | 5001 | ❌ |
| LOG_LEVEL | 日志级别 | INFO | ❌ |

## 🔧 常见问题

**Q: 如何获取Bot Token？**
A: 在Telegram搜索 @BotFather，使用 `/newbot` 创建Bot

**Q: 如何获取群组ID？**
A: 运行 `python tools/get_chat_id.py`

**Q: 端口被占用？**
A: 在 `.env` 中修改 `API_PORT=5002`

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📚 相关文档

- [API完整文档](docs/API.md)
- [部署指南](docs/DEPLOYMENT.md)
- [Telegram Bot API](https://core.telegram.org/bots/api)
