# API使用示例

## 快速开始

### 1. 启动API服务器

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动服务器（默认端口5001）
python api_server.py
```

服务器启动后会显示：
```
✅ Bot连接成功: @TestForJoJoBot
🚀 API服务器启动在 http://0.0.0.0:5001
```

### 2. 使用curl测试

#### 发送简单消息
```bash
curl -X POST http://localhost:5001/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from API!"}'
```

#### 发送Markdown格式消息
```bash
curl -X POST http://localhost:5001/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "**粗体文本**\n\n*斜体文本*\n\n`代码文本`"
  }'
```

#### 发送到指定群组
```bash
curl -X POST http://localhost:5001/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "发送到特定群组",
    "chat_id": -4983226585
  }'
```

#### 发送格式化交易信号
```bash
curl -X POST http://localhost:5001/send/formatted \
  -H "Content-Type: application/json" \
  -d '{
    "chain": "Ethereum",
    "token": "USDT",
    "amount": 10000,
    "action": "买入",
    "from_address": "0x1234567890abcdef",
    "to_address": "0xabcdefabcdef1234",
    "tx_hash": "0xdeadbeef12345678",
    "timestamp": "2025-10-18 22:45:00"
  }'
```

---

## Python集成示例

### 示例1: 简单发送

```python
import requests

def send_simple_message(message):
    """发送简单消息"""
    url = "http://localhost:5001/send"
    data = {
        "message": message
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        result = response.json()
        print(f"✅ 发送成功: {result}")
    else:
        print(f"❌ 发送失败: {response.text}")

# 使用
send_simple_message("**测试消息**\n这是一条测试消息")
```

### 示例2: DEX交易监控

```python
import requests
from datetime import datetime

def send_dex_signal(chain, token, amount, action, tx_data):
    """发送DEX交易信号"""
    url = "http://localhost:5001/send/formatted"

    data = {
        "chain": chain,
        "token": token,
        "amount": amount,
        "action": action,
        "from_address": tx_data.get('from'),
        "to_address": tx_data.get('to'),
        "tx_hash": tx_data.get('hash'),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        print(f"✅ 交易信号已发送: {token}")
        return True
    else:
        print(f"❌ 发送失败: {response.text}")
        return False

# 使用示例
tx_data = {
    'from': '0x1234567890abcdef',
    'to': '0xabcdefabcdef1234',
    'hash': '0xdeadbeef12345678'
}

send_dex_signal(
    chain="Ethereum",
    token="USDT",
    amount=10000,
    action="买入",
    tx_data=tx_data
)
```

### 示例3: 批量发送到多个群组

```python
import requests

def send_to_multiple_groups(message, group_ids):
    """批量发送到多个群组"""
    url = "http://localhost:5001/send/multiple"

    data = {
        "message": message,
        "chat_ids": group_ids
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功发送: {result['sent_count']} 个群组")
        print(f"❌ 失败: {result['failed_count']} 个群组")
        return result
    else:
        print(f"❌ 请求失败: {response.text}")
        return None

# 使用示例
group_ids = [-4983226585, -4843903998]
send_to_multiple_groups("📢 重要通知：系统更新", group_ids)
```

### 示例4: 完整的监控系统

```python
import requests
import time
from datetime import datetime

class TelegramNotifier:
    """Telegram通知器类"""

    def __init__(self, api_url="http://localhost:5001"):
        self.api_url = api_url
        self.default_chat_id = None

    def set_default_chat(self, chat_id):
        """设置默认群组"""
        self.default_chat_id = chat_id

    def send(self, message, chat_id=None):
        """发送消息"""
        url = f"{self.api_url}/send"
        data = {"message": message}

        if chat_id:
            data["chat_id"] = chat_id
        elif self.default_chat_id:
            data["chat_id"] = self.default_chat_id

        try:
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"发送失败: {e}")
            return False

    def send_trade_alert(self, trade_info):
        """发送交易提醒"""
        url = f"{self.api_url}/send/formatted"

        data = {
            "chain": trade_info.get('chain', 'Unknown'),
            "token": trade_info.get('token', 'Unknown'),
            "amount": trade_info.get('amount', 0),
            "action": trade_info.get('action', 'Trade'),
            "from_address": trade_info.get('from_address', 'N/A'),
            "to_address": trade_info.get('to_address', 'N/A'),
            "tx_hash": trade_info.get('tx_hash', 'N/A'),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"发送交易提醒失败: {e}")
            return False


# 使用示例
if __name__ == '__main__':
    # 创建通知器
    notifier = TelegramNotifier()
    notifier.set_default_chat(-4983226585)

    # 发送启动消息
    notifier.send("🚀 **监控系统已启动**\n\n等待交易信号...")

    # 模拟监控循环
    while True:
        # 这里应该是你的实际监控逻辑
        # 检测到交易时发送通知
        trade_detected = False  # 你的检测逻辑

        if trade_detected:
            trade_info = {
                'chain': 'Ethereum',
                'token': 'USDT',
                'amount': 10000,
                'action': '买入',
                'from_address': '0x1234...',
                'to_address': '0xabcd...',
                'tx_hash': '0xdead...'
            }
            notifier.send_trade_alert(trade_info)

        time.sleep(10)  # 每10秒检查一次
```

---

## JavaScript/Node.js集成

### 使用axios

```javascript
const axios = require('axios');

// 发送消息
async function sendMessage(message, chatId = null) {
    try {
        const response = await axios.post('http://localhost:5001/send', {
            message: message,
            ...(chatId && { chat_id: chatId })
        });

        console.log('✅ 发送成功:', response.data);
        return true;
    } catch (error) {
        console.error('❌ 发送失败:', error.response?.data || error.message);
        return false;
    }
}

// 发送交易信号
async function sendTradeSignal(tradeData) {
    try {
        const response = await axios.post('http://localhost:5001/send/formatted', {
            chain: tradeData.chain,
            token: tradeData.token,
            amount: tradeData.amount,
            action: tradeData.action,
            from_address: tradeData.fromAddress,
            to_address: tradeData.toAddress,
            tx_hash: tradeData.txHash,
            timestamp: new Date().toISOString()
        });

        console.log('✅ 交易信号已发送');
        return true;
    } catch (error) {
        console.error('❌ 发送失败:', error.message);
        return false;
    }
}

// 使用示例
sendMessage('**Hello from Node.js!**');

sendTradeSignal({
    chain: 'Ethereum',
    token: 'USDT',
    amount: 10000,
    action: 'Buy',
    fromAddress: '0x1234...',
    toAddress: '0xabcd...',
    txHash: '0xdead...'
});
```

---

## 高级用法

### 错误重试机制

```python
import requests
import time

def send_with_retry(message, max_retries=3):
    """带重试的发送"""
    url = "http://localhost:5001/send"

    for attempt in range(max_retries):
        try:
            response = requests.post(url, json={"message": message}, timeout=10)

            if response.status_code == 200:
                print(f"✅ 发送成功 (尝试 {attempt + 1})")
                return True

            print(f"⚠️  发送失败 (尝试 {attempt + 1}): {response.text}")

        except Exception as e:
            print(f"❌ 请求异常 (尝试 {attempt + 1}): {e}")

        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # 指数退避

    print("❌ 所有重试均失败")
    return False
```

### 消息队列

```python
import queue
import threading
import requests
import time

class MessageQueue:
    """消息队列处理器"""

    def __init__(self, api_url="http://localhost:5001"):
        self.api_url = api_url
        self.queue = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self._process_queue)
        self.thread.daemon = True
        self.thread.start()

    def add_message(self, message, chat_id=None):
        """添加消息到队列"""
        self.queue.put({"message": message, "chat_id": chat_id})

    def _process_queue(self):
        """处理队列中的消息"""
        while self.running:
            try:
                if not self.queue.empty():
                    data = self.queue.get()
                    self._send(data)
                    time.sleep(0.1)  # 避免发送过快
                else:
                    time.sleep(0.5)
            except Exception as e:
                print(f"队列处理错误: {e}")

    def _send(self, data):
        """发送消息"""
        try:
            response = requests.post(f"{self.api_url}/send", json=data, timeout=10)
            if response.status_code == 200:
                print(f"✅ 消息已发送: {data['message'][:30]}...")
            else:
                print(f"❌ 发送失败")
        except Exception as e:
            print(f"❌ 发送异常: {e}")

    def stop(self):
        """停止队列处理"""
        self.running = False
        self.thread.join()


# 使用示例
mq = MessageQueue()
mq.add_message("消息1")
mq.add_message("消息2")
mq.add_message("消息3")

# 程序结束时
# mq.stop()
```

---

## 完整项目集成示例

```python
# dex_monitor.py
import requests
import time
from datetime import datetime

class DEXMonitor:
    """DEX交易监控器"""

    def __init__(self, telegram_api_url="http://localhost:5001"):
        self.api_url = telegram_api_url
        self.running = False

    def start(self):
        """启动监控"""
        self.running = True
        self.notify("🚀 **DEX监控启动**\n\n系统正在监控交易...")

        while self.running:
            try:
                # 你的监控逻辑
                transactions = self.check_transactions()

                for tx in transactions:
                    self.notify_transaction(tx)

                time.sleep(5)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"监控错误: {e}")
                time.sleep(10)

        self.notify("⏹️ **DEX监控已停止**")

    def check_transactions(self):
        """检查交易 (示例)"""
        # 这里实现你的实际监控逻辑
        # 返回检测到的交易列表
        return []

    def notify(self, message):
        """发送通知"""
        try:
            response = requests.post(
                f"{self.api_url}/send",
                json={"message": message},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"通知失败: {e}")
            return False

    def notify_transaction(self, tx):
        """发送交易通知"""
        try:
            response = requests.post(
                f"{self.api_url}/send/formatted",
                json=tx,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"交易通知失败: {e}")
            return False


if __name__ == '__main__':
    monitor = DEXMonitor()
    monitor.start()
```

---

查看 `API_GUIDE.md` 获取完整API文档。
