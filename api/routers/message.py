"""
消息发送路由
处理所有消息发送相关的API端点
"""
import asyncio
from flask import Blueprint, request, jsonify
from api.config import settings
from api.utils.logger import logger
from api.utils.message_formatter import (
    format_whale_trade_from_dict,
    format_liquidation_from_dict
)

message_bp = Blueprint('message', __name__, url_prefix='/api/v1')

# 全局Telegram发送器实例（将在app初始化时设置）
telegram_sender = None


def set_telegram_sender(sender):
    """设置Telegram发送器实例"""
    global telegram_sender
    telegram_sender = sender


@message_bp.route('/send', methods=['POST'])
def send_message():
    """
    发送消息接口

    Body:
        {
            "message": "消息内容",
            "chat_id": -1234567890,  // 可选，优先级最高
            "language": "zh",  // 可选，'zh', 'en', 'both'
            "parse_mode": "Markdown"  // 可选
        }
    """
    if not telegram_sender:
        return jsonify({
            'success': False,
            'error': 'Telegram sender not initialized'
        }), 500

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body cannot be empty'
            }), 400

        message = data.get('message')
        if not message:
            return jsonify({
                'success': False,
                'error': 'Missing message parameter'
            }), 400

        # 获取目标群组ID
        # 优先级：chat_id > language > default
        chat_id = data.get('chat_id')
        language = data.get('language')

        if not chat_id:
            if language == 'both':
                # 发送到所有群组
                return send_to_both_groups(message, data.get('parse_mode', 'Markdown'))
            elif language:
                # 根据语言选择群组
                chat_id = settings.get_chat_id(language)
            else:
                # 使用默认群组
                chat_id = settings.DEFAULT_CHAT_ID

        if not chat_id:
            return jsonify({
                'success': False,
                'error': 'Missing chat_id parameter and no default chat configured'
            }), 400

        # 转换chat_id
        try:
            if isinstance(chat_id, str) and not chat_id.startswith('@'):
                chat_id = int(chat_id)
        except ValueError:
            pass

        parse_mode = data.get('parse_mode', 'Markdown')

        # 发送消息
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(
            telegram_sender.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode
            )
        )

        if success:
            logger.info(f"✅ Message sent to chat {chat_id}")
            return jsonify({
                'success': True,
                'message': 'Message sent successfully',
                'chat_id': chat_id,
                'language': language
            }), 200
        else:
            logger.error(f"❌ Failed to send message to chat {chat_id}")
            return jsonify({
                'success': False,
                'error': 'Failed to send message'
            }), 500

    except Exception as e:
        logger.error(f"❌ Error processing request: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def send_to_both_groups(message: str, parse_mode: str = 'Markdown'):
    """发送到中英文两个群组"""
    chat_ids = settings.get_all_chat_ids()

    if not chat_ids:
        return jsonify({
            'success': False,
            'error': 'No chat groups configured'
        }), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(
        telegram_sender.send_to_multiple_chats(
            chat_ids=chat_ids,
            text=message,
            parse_mode=parse_mode
        )
    )

    logger.info(f"✅ Batch send to both groups - success: {len(result['success'])}, failed: {len(result['failed'])}")

    return jsonify({
        'success': True,
        'message': 'Message sent to both groups',
        'sent_count': len(result['success']),
        'failed_count': len(result['failed']),
        'results': result
    }), 200


@message_bp.route('/send/multiple', methods=['POST'])
def send_to_multiple():
    """
    批量发送消息

    Body:
        {
            "message": "消息内容",
            "chat_ids": [-1234567890, -9876543210],
            "parse_mode": "Markdown"
        }
    """
    if not telegram_sender:
        return jsonify({
            'success': False,
            'error': 'Telegram sender not initialized'
        }), 500

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body cannot be empty'
            }), 400

        message = data.get('message')
        if not message:
            return jsonify({
                'success': False,
                'error': 'Missing message parameter'
            }), 400

        chat_ids = data.get('chat_ids')
        if not chat_ids or not isinstance(chat_ids, list):
            return jsonify({
                'success': False,
                'error': 'chat_ids must be an array'
            }), 400

        # 转换chat_ids
        processed_chat_ids = []
        for chat_id in chat_ids:
            try:
                if isinstance(chat_id, str) and not chat_id.startswith('@'):
                    processed_chat_ids.append(int(chat_id))
                else:
                    processed_chat_ids.append(chat_id)
            except ValueError:
                processed_chat_ids.append(chat_id)

        parse_mode = data.get('parse_mode', 'Markdown')

        # 批量发送
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            telegram_sender.send_to_multiple_chats(
                chat_ids=processed_chat_ids,
                text=message,
                parse_mode=parse_mode
            )
        )

        logger.info(f"✅ Batch send completed - success: {len(result['success'])}, failed: {len(result['failed'])}")

        return jsonify({
            'success': True,
            'sent_count': len(result['success']),
            'failed_count': len(result['failed']),
            'results': result
        }), 200

    except Exception as e:
        logger.error(f"❌ Error in batch send: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@message_bp.route('/send/formatted', methods=['POST'])
def send_formatted_message():
    """
    发送格式化的交易信号消息

    Body:
        {
            "chain": "Ethereum",
            "token": "USDT",
            "amount": 10000,
            "action": "买入",
            "from_address": "0x1234...5678",
            "to_address": "0xabcd...ef00",
            "tx_hash": "0xdeadbeef...",
            "chat_id": -1234567890
        }
    """
    if not telegram_sender:
        return jsonify({
            'success': False,
            'error': 'Telegram sender not initialized'
        }), 500

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body cannot be empty'
            }), 400

        # 构建格式化消息
        chain = data.get('chain', 'Unknown')
        token = data.get('token', 'Unknown')
        amount = data.get('amount', 0)
        action = data.get('action', 'Trade')
        from_addr = data.get('from_address', 'N/A')
        to_addr = data.get('to_address', 'N/A')
        tx_hash = data.get('tx_hash', 'N/A')

        message = f"""
⚡ **DEX Trading Signal**

🔹 **Chain**: {chain}
💰 **Token**: {token}
📊 **Amount**: {amount:,.2f}
📈 **Action**: {action}

🔗 **Transaction Details**:
  • From: `{from_addr}`
  • To: `{to_addr}`
  • Hash: `{tx_hash}`

⏰ Time: {data.get('timestamp', 'N/A')}
        """.strip()

        chat_id = data.get('chat_id', settings.DEFAULT_CHAT_ID)
        if not chat_id:
            return jsonify({
                'success': False,
                'error': 'Missing chat_id parameter'
            }), 400

        try:
            if isinstance(chat_id, str) and not chat_id.startswith('@'):
                chat_id = int(chat_id)
        except ValueError:
            pass

        # 发送消息
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(
            telegram_sender.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )
        )

        if success:
            return jsonify({
                'success': True,
                'message': 'Trading signal sent successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send message'
            }), 500

    except Exception as e:
        logger.error(f"❌ Error sending formatted message: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
