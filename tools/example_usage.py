"""
Telegram消息发送示例
演示如何使用 tg_sender 模块
"""
import asyncio
import logging
from tg_sender import TelegramSender, send_telegram_message

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def example_basic_usage():
    """示例1: 基础用法 - 发送单条消息"""
    print("\n=== 示例1: 基础用法 ===\n")

    # 配置
    BOT_TOKEN = "your_bot_token_here"  # 替换为你的Bot Token
    CHAT_ID = -1001234567890  # 替换为你的群组ID

    # 创建发送器
    sender = TelegramSender(bot_token=BOT_TOKEN)

    # 初始化
    if not await sender.initialize():
        print("❌ Bot初始化失败")
        return

    # 发送消息
    message = """
🔔 **测试消息**

这是一条测试消息
✅ 支持Markdown格式
💡 可以发送各种格式的内容

`代码块示例`
    """

    success = await sender.send_message(
        chat_id=CHAT_ID,
        text=message.strip()
    )

    if success:
        print("✅ 消息发送成功")
    else:
        print("❌ 消息发送失败")

    # 关闭连接
    await sender.close()


async def example_multiple_chats():
    """示例2: 向多个群组发送消息"""
    print("\n=== 示例2: 批量发送 ===\n")

    BOT_TOKEN = "your_bot_token_here"
    CHAT_IDS = [
        -1001234567890,  # 群组1
        -1009876543210,  # 群组2
        # 可以添加更多群组ID
    ]

    sender = TelegramSender(bot_token=BOT_TOKEN)
    await sender.initialize()

    message = """
📢 **批量通知**

这是发送到多个群组的消息
📊 测试批量发送功能
    """

    result = await sender.send_to_multiple_chats(
        chat_ids=CHAT_IDS,
        text=message.strip()
    )

    print(f"✅ 成功发送: {len(result['success'])} 个群组")
    print(f"❌ 发送失败: {len(result['failed'])} 个群组")

    await sender.close()


async def example_formatted_message():
    """示例3: 发送格式化的交易消息"""
    print("\n=== 示例3: 格式化消息 ===\n")

    BOT_TOKEN = "your_bot_token_here"
    CHAT_ID = -1001234567890

    sender = TelegramSender(bot_token=BOT_TOKEN)
    await sender.initialize()

    # 模拟交易数据
    transaction_data = {
        'chain': 'Ethereum',
        'token_symbol': 'USDT',
        'amount': 10000,
        'from_address': '0x1234...5678',
        'to_address': '0xabcd...ef00',
        'tx_hash': '0xdeadbeef...'
    }

    # 格式化消息
    message = f"""
⧫ **{transaction_data['chain']} 交易监控**

💰 **代币**: {transaction_data['token_symbol']}
📊 **数量**: {transaction_data['amount']:,.2f}
📤 **发送方**: `{transaction_data['from_address']}`
📥 **接收方**: `{transaction_data['to_address']}`
🔗 **交易哈希**: `{transaction_data['tx_hash']}`

🔍 [查看交易详情](https://etherscan.io/tx/{transaction_data['tx_hash']})
    """

    success = await sender.send_message(
        chat_id=CHAT_ID,
        text=message.strip()
    )

    print("✅ 交易消息发送成功" if success else "❌ 交易消息发送失败")

    await sender.close()


async def example_quick_send():
    """示例4: 使用便捷函数快速发送"""
    print("\n=== 示例4: 便捷函数 ===\n")

    BOT_TOKEN = "your_bot_token_here"
    CHAT_ID = -1001234567890

    # 一行代码发送消息
    success = await send_telegram_message(
        bot_token=BOT_TOKEN,
        chat_id=CHAT_ID,
        text="⚡ **快速消息**\n使用便捷函数发送"
    )

    print("✅ 快速发送成功" if success else "❌ 快速发送失败")


async def example_test_connection():
    """示例5: 测试Bot连接"""
    print("\n=== 示例5: 测试连接 ===\n")

    BOT_TOKEN = "your_bot_token_here"
    CHAT_ID = -1001234567890

    sender = TelegramSender(bot_token=BOT_TOKEN)
    await sender.initialize()

    # 测试连接
    is_connected = await sender.test_connection(CHAT_ID)

    if is_connected:
        print("✅ Bot连接正常，可以发送消息")
    else:
        print("❌ Bot连接失败或无权限发送到该群组")

    await sender.close()


async def example_error_handling():
    """示例6: 错误处理"""
    print("\n=== 示例6: 错误处理 ===\n")

    BOT_TOKEN = "your_bot_token_here"
    INVALID_CHAT_ID = -1000000000000  # 不存在的群组

    sender = TelegramSender(bot_token=BOT_TOKEN)
    await sender.initialize()

    # 尝试发送到不存在的群组
    success = await sender.send_message(
        chat_id=INVALID_CHAT_ID,
        text="测试错误处理",
        retry_count=2  # 只重试2次
    )

    if not success:
        print("⚠️ 消息发送失败（预期行为）")
        print("💡 系统会自动处理错误并记录日志")

    await sender.close()


async def main():
    """运行所有示例"""
    print("🚀 Telegram消息发送示例")
    print("=" * 50)

    # 提示用户修改配置
    print("\n⚠️ 请先在各个示例函数中修改以下配置：")
    print("  - BOT_TOKEN: 你的Bot Token")
    print("  - CHAT_ID: 目标群组ID")
    print("\n然后取消注释要运行的示例\n")

    # 取消注释下面的行来运行对应示例
    # await example_basic_usage()
    # await example_multiple_chats()
    # await example_formatted_message()
    # await example_quick_send()
    # await example_test_connection()
    # await example_error_handling()


if __name__ == '__main__':
    asyncio.run(main())
