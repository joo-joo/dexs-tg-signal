"""
简化版获取群组ID工具
直接使用Bot API的getUpdates方法，避免event loop问题

使用方法：
1. 将Bot添加到你的群组
2. 在群组中发送任意消息
3. 运行此脚本查看群组ID
"""
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()


def get_chat_ids():
    """获取所有与Bot交互的chat ID"""
    bot_token = os.getenv('BOT_TOKEN')

    if not bot_token:
        print("❌ 错误: 请先在.env文件中配置 BOT_TOKEN")
        return

    print("\n" + "=" * 60)
    print("🤖 Telegram Chat ID 获取工具 (简化版)")
    print("=" * 60)
    print("\n📝 使用说明:")
    print("1. 将Bot添加到你的群组")
    print("2. 在群组中发送任意消息（比如: hello）")
    print("3. 此脚本会显示群组ID")
    print("\n⏳ 正在获取最近的消息...")
    print("=" * 60 + "\n")

    # 获取Bot信息
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            bot_info = response.json()['result']
            print(f"✅ Bot连接成功: @{bot_info['username']}")
            print()
        else:
            print(f"❌ Bot验证失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return

    # 获取更新
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        params = {
            'offset': -100,  # 获取最近100条消息
            'timeout': 0
        }
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"❌ 获取消息失败: {response.text}")
            return

        updates = response.json()['result']

        if not updates:
            print("⚠️  未找到任何消息")
            print("\n💡 请确保:")
            print("   1. Bot已被添加到群组")
            print("   2. 在群组中发送了消息")
            print("   3. 消息是最近发送的（最近100条内）")
            print("\n🔄 尝试现在在群组中发送一条消息，然后再次运行此脚本")
            return

        # 收集所有不同的chat
        chats = {}
        for update in updates:
            if 'message' in update:
                chat = update['message']['chat']
                chat_id = chat['id']
                chat_type = chat['type']
                chat_title = chat.get('title', chat.get('username', chat.get('first_name', 'Unknown')))

                if chat_id not in chats:
                    chats[chat_id] = {
                        'id': chat_id,
                        'type': chat_type,
                        'title': chat_title
                    }

        # 显示找到的chats
        print(f"📊 找到 {len(chats)} 个聊天\n")

        group_found = False
        for chat_id, chat_info in chats.items():
            print("=" * 60)
            print(f"💬 聊天类型: {chat_info['type']}")
            print(f"🆔 Chat ID: {chat_info['id']}")
            print(f"📝 名称: {chat_info['title']}")

            if chat_info['type'] in ['group', 'supergroup']:
                group_found = True
                print("\n✅ 这是一个群组！")
                print(f"📋 请将以下配置添加到.env文件:")
                print(f"   CHAT_ID={chat_info['id']}")
            elif chat_info['type'] == 'channel':
                print("\n✅ 这是一个频道！")
                print(f"📋 请将以下配置添加到.env文件:")
                print(f"   CHAT_ID={chat_info['id']}")
            elif chat_info['type'] == 'private':
                print("\n💡 这是私聊")

            print("=" * 60 + "\n")

        if group_found:
            print("🎉 成功找到群组！请复制上面的CHAT_ID到.env文件")
        else:
            print("⚠️  未找到群组聊天")
            print("💡 请在群组中发送消息后重试")

    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == '__main__':
    get_chat_ids()
