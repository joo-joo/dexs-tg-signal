# 快速开始指南

## 5分钟上手Telegram消息发送

### 第一步：安装依赖

```bash
pip install -r requirements.txt
```

### 第二步：配置Bot

1. **创建Telegram Bot**
   - 在Telegram中搜索 @BotFather
   - 发送 `/newbot` 并按提示操作
   - 获得你的Bot Token（类似：`1234567890:ABCdefGHI...`）

2. **获取群组ID**
   - 创建一个Telegram群组
   - 将你的Bot添加到群组
   - 搜索 @userinfobot 并将它也加入群组
   - 它会显示群组ID（类似：`-1001234567890`）

3. **配置环境变量**
   ```bash
   cp .env.example .env
   ```

   编辑 `.env` 文件，填入你的配置：
   ```
   BOT_TOKEN=你的Bot_Token
   CHAT_ID=你的群组ID
   ```

### 第三步：测试发送

运行测试脚本：
```bash
python test_sender.py
```

如果看到 "✅ 所有测试通过！Bot功能正常！"，说明配置成功！

### 第四步：开始使用

**方式1: 简单发送**
```python
import asyncio
from tg_sender import send_telegram_message

async def main():
    await send_telegram_message(
        bot_token="你的Token",
        chat_id=-1001234567890,
        text="**Hello!** 这是我的第一条消息"
    )

asyncio.run(main())
```

**方式2: 使用类**
```python
import asyncio
from tg_sender import TelegramSender

async def main():
    sender = TelegramSender(bot_token="你的Token")
    await sender.initialize()

    await sender.send_message(
        chat_id=-1001234567890,
        text="**Hello!** 使用类发送消息"
    )

    await sender.close()

asyncio.run(main())
```

### 更多示例

查看 `example_usage.py` 了解更多用法：
- 批量发送到多个群组
- 发送格式化的交易消息
- 错误处理
- 等等...

### 常见问题

**Q: "Chat not found" 错误**
A: 确保Bot已加入群组，且群组ID正确（负数开头）

**Q: 消息发送失败**
A: 检查Bot是否有发送消息权限（在群组设置中查看）

**Q: "Unauthorized" 错误**
A: Bot Token不正确，请检查是否完整复制

### 下一步

- 阅读 [完整文档](README.md) 了解所有功能
- 查看 [示例代码](example_usage.py) 学习高级用法
- 根据你的需求定制消息格式

---

🎉 现在你已经可以使用Telegram Bot发送消息了！
