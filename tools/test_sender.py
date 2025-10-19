"""
快速测试脚本
用于验证Telegram Bot发送功能是否正常
"""
import asyncio
import logging
import os
from dotenv import load_dotenv
from tg_sender import TelegramSender

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def test_basic_send():
    """测试基本发送功能"""
    # 从环境变量读取配置
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')

    if not bot_token or not chat_id:
        print("❌ 错误: 请先在.env文件中配置 BOT_TOKEN 和 CHAT_ID")
        print("提示: 复制 .env.example 为 .env 并填入正确的值")
        return

    try:
        chat_id = int(chat_id)
    except ValueError:
        # 如果不是数字，可能是频道用户名
        pass

    print(f"🤖 Bot Token: {bot_token[:10]}...")
    print(f"📢 目标群组: {chat_id}")
    print("=" * 50)

    # 创建发送器
    sender = TelegramSender(bot_token=bot_token)

    # 测试初始化
    print("\n1️⃣ 测试Bot初始化...")
    if not await sender.initialize():
        print("❌ Bot初始化失败，请检查Token是否正确")
        return
    print("✅ Bot初始化成功")

    # 测试连接
    print("\n2️⃣ 测试Bot连接...")
    if not await sender.test_connection(chat_id):
        print("❌ 连接测试失败，请检查:")
        print("   - 群组ID是否正确")
        print("   - Bot是否已加入该群组")
        print("   - Bot是否有发送消息权限")
        await sender.close()
        return
    print("✅ 连接测试成功")

    # 发送测试消息
    print("\n3️⃣ 发送测试消息...")
    test_message = """
🎉 **Telegram Bot 测试成功！**

✅ Bot初始化正常
✅ 连接测试通过
✅ 消息发送成功

🚀 现在你可以使用这个模块发送消息了！

---
_测试时间: {time}_
    """.format(time=asyncio.get_event_loop().time())

    success = await sender.send_message(
        chat_id=chat_id,
        text=test_message.strip()
    )

    if success:
        print("✅ 测试消息发送成功")
    else:
        print("❌ 测试消息发送失败")

    # 关闭连接
    print("\n4️⃣ 关闭连接...")
    await sender.close()
    print("✅ 测试完成")

    print("\n" + "=" * 50)
    print("🎊 所有测试通过！Bot功能正常！")


async def test_formatted_message():
    """测试发送格式化消息"""
    bot_token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')

    if not bot_token or not chat_id:
        print("❌ 请先配置 .env 文件")
        return

    try:
        chat_id = int(chat_id)
    except ValueError:
        pass

    sender = TelegramSender(bot_token=bot_token)
    await sender.initialize()

    # 发送格式化的交易提醒消息
    message = """
⚡ **DEX 交易信号**

🔹 **链**: Ethereum
💰 **代币**: USDT
📊 **交易额**: $10,000.00
📈 **类型**: 买入

🔗 **交易详情**:
  • 买方: `0x1234...5678`
  • 卖方: `0xabcd...ef00`
  • Gas: 21 Gwei
  • 哈希: `0xdead...beef`

🔍 [在 Etherscan 查看](https://etherscan.io/tx/0xdeadbeef)

⏰ 时间: 2025-10-18 22:15:30
    """

    await sender.send_message(
        chat_id=chat_id,
        text=message.strip()
    )

    print("✅ 格式化消息发送完成")
    await sender.close()


async def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("🤖 Telegram Bot 发送功能测试")
    print("=" * 50)

    # 运行基础测试
    await test_basic_send()

    # 如果基础测试通过，可以取消注释下面的行测试格式化消息
    # print("\n" + "=" * 50)
    # print("📝 测试格式化消息")
    # print("=" * 50)
    # await test_formatted_message()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        logger.exception("测试失败")
