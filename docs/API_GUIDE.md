# Telegram消息发送API文档

## 概述

提供HTTP API接口，可以通过POST请求发送消息到Telegram群组。

## 启动服务

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动API服务器
python api_server.py
```

默认运行在 `http://localhost:5000`

## API接口

### 1. 健康检查

**接口**: `GET /health`

**描述**: 检查服务是否正常运行

**返回示例**:
```json
{
  "status": "ok",
  "service": "telegram-sender",
  "telegram_ready": true
}
```

**测试命令**:
```bash
curl http://localhost:5000/health
```

---

### 2. 发送消息

**接口**: `POST /send`

**描述**: 发送消息到指定或默认的Telegram群组

**请求体**:
```json
{
  "message": "消息内容",
  "chat_id": -1234567890,
  "parse_mode": "Markdown"
}
```

**参数说明**:
- `message` (必填): 消息文本内容
- `chat_id` (可选): 目标群组ID，不提供则使用环境变量中的默认群组
- `parse_mode` (可选): 解析模式，支持 `Markdown`、`HTML` 或 `None`，默认 `Markdown`

**返回示例**:
```json
{
  "success": true,
  "message": "消息发送成功",
  "chat_id": -1234567890
}
```

**测试命令**:
```bash
# 发送简单消息（使用默认群组）
curl -X POST http://localhost:5000/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from API!"}'

# 发送Markdown格式消息
curl -X POST http://localhost:5000/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "**粗体** *斜体* `代码`",
    "chat_id": -4983226585
  }'
```

---

### 3. 批量发送

**接口**: `POST /send/multiple`

**描述**: 同时发送消息到多个群组

**请求体**:
```json
{
  "message": "消息内容",
  "chat_ids": [-1234567890, -9876543210],
  "parse_mode": "Markdown"
}
```

**参数说明**:
- `message` (必填): 消息文本内容
- `chat_ids` (必填): 目标群组ID数组
- `parse_mode` (可选): 解析模式，默认 `Markdown`

**返回示例**:
```json
{
  "success": true,
  "sent_count": 2,
  "failed_count": 0,
  "results": {
    "success": [-1234567890, -9876543210],
    "failed": []
  }
}
```

**测试命令**:
```bash
curl -X POST http://localhost:5000/send/multiple \
  -H "Content-Type: application/json" \
  -d '{
    "message": "批量通知消息",
    "chat_ids": [-4983226585, -4843903998]
  }'
```

---

### 4. 发送格式化交易信号

**接口**: `POST /send/formatted`

**描述**: 发送格式化的DEX交易信号消息

**请求体**:
```json
{
  "chain": "Ethereum",
  "token": "USDT",
  "amount": 10000,
  "action": "买入",
  "from_address": "0x1234...5678",
  "to_address": "0xabcd...ef00",
  "tx_hash": "0xdeadbeef...",
  "timestamp": "2025-10-18 22:30:00",
  "chat_id": -1234567890
}
```

**参数说明**:
- `chain` (可选): 区块链名称，默认 `Unknown`
- `token` (可选): 代币符号，默认 `Unknown`
- `amount` (可选): 交易数量，默认 `0`
- `action` (可选): 操作类型（买入/卖出），默认 `交易`
- `from_address` (可选): 发送方地址
- `to_address` (可选): 接收方地址
- `tx_hash` (可选): 交易哈希
- `timestamp` (可选): 时间戳
- `chat_id` (可选): 目标群组ID

**返回示例**:
```json
{
  "success": true,
  "message": "交易信号发送成功"
}
```

**测试命令**:
```bash
curl -X POST http://localhost:5000/send/formatted \
  -H "Content-Type: application/json" \
  -d '{
    "chain": "Ethereum",
    "token": "USDT",
    "amount": 10000,
    "action": "买入",
    "from_address": "0x1234567890abcdef",
    "to_address": "0xabcdefabcdef1234",
    "tx_hash": "0xdeadbeef12345678",
    "timestamp": "2025-10-18 22:30:00"
  }'
```

---

## 错误处理

所有接口在出错时返回如下格式：

```json
{
  "success": false,
  "error": "错误描述"
}
```

常见错误：
- `400`: 请求参数错误
- `500`: 服务器内部错误（Telegram发送失败等）

---

## Python调用示例

```python
import requests

# 1. 发送简单消息
response = requests.post('http://localhost:5000/send', json={
    'message': '**测试消息**\n这是一条测试消息'
})
print(response.json())

# 2. 发送到指定群组
response = requests.post('http://localhost:5000/send', json={
    'message': 'Hello!',
    'chat_id': -4983226585
})

# 3. 批量发送
response = requests.post('http://localhost:5000/send/multiple', json={
    'message': '批量通知',
    'chat_ids': [-4983226585, -4843903998]
})

# 4. 发送格式化交易信号
response = requests.post('http://localhost:5000/send/formatted', json={
    'chain': 'Ethereum',
    'token': 'USDT',
    'amount': 10000,
    'action': '买入',
    'from_address': '0x1234...5678',
    'to_address': '0xabcd...ef00',
    'tx_hash': '0xdeadbeef...'
})
```

---

## 环境变量配置

在 `.env` 文件中配置：

```env
# Telegram配置（必需）
BOT_TOKEN=your_bot_token
CHAT_ID=-1234567890

# API服务器配置（可选）
API_HOST=0.0.0.0
API_PORT=5000
```

---

## 部署建议

### 开发环境
```bash
python api_server.py
```

### 生产环境（使用gunicorn）

1. 安装gunicorn:
```bash
pip install gunicorn
```

2. 启动服务:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

参数说明：
- `-w 4`: 4个worker进程
- `-b 0.0.0.0:5000`: 绑定到所有网卡的5000端口

### Docker部署

创建 `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "api_server.py"]
```

构建和运行:
```bash
docker build -t telegram-api .
docker run -p 5000:5000 --env-file .env telegram-api
```

---

## 安全建议

1. **使用API密钥**: 在生产环境中添加认证机制
2. **限流**: 防止API被滥用
3. **HTTPS**: 使用反向代理（如Nginx）添加SSL
4. **IP白名单**: 限制可访问的IP地址

---

## 常见问题

**Q: 消息发送失败？**
A: 检查Bot是否在群组中，群组ID是否正确

**Q: 如何发送图片？**
A: 当前版本只支持文本，需要扩展API添加 `send_photo` 接口

**Q: 并发请求会有问题吗？**
A: 当前实现为同步处理，建议使用gunicorn多worker或实现异步处理

**Q: 如何监控API状态？**
A: 使用 `/health` 接口进行健康检查
