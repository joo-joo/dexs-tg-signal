"""
巨鲸交易和清算消息路由
"""
import asyncio
from flask import Blueprint, request, jsonify
from api.config import settings
from api.utils.logger import logger
from api.utils.message_formatter import (
    format_whale_trade_from_dict,
    format_liquidation_from_dict
)


# 参数映射字典
ACTION_MAP = {
    1: {'zh': '买入', 'en': 'Long'},
    2: {'zh': '卖出', 'en': 'Short'}
}

DIRECTION_MAP = {
    1: {'zh': '做多 (Long)', 'en': 'Long'},
    2: {'zh': '做空 (Short)', 'en': 'Short'}
}

POSITION_TYPE_MAP = {
    1: {'zh': '做多', 'en': 'Long'},
    2: {'zh': '做空', 'en': 'Short'}
}

MESSAGE_TYPE_MAP = {
    1: 'trade',      # 交易
    2: 'liquidation' # 强平
}

whale_bp = Blueprint('whale', __name__, url_prefix='/api/v1/whale')

# 全局Telegram发送器实例
telegram_sender = None


def set_telegram_sender(sender):
    """设置Telegram发送器实例"""
    global telegram_sender
    telegram_sender = sender


@whale_bp.route('/send', methods=['POST'])
def send_whale_message():
    """
    统一的巨鲸消息发送接口（支持交易和清算）

    自动发送到中英文两个群组，中文群组收到中文格式，英文群组收到英文格式。

    Body:
        {
            "message_type": 1,  // 必需: 1=交易, 2=强平
            "action": 1,  // 交易时必需: 1=买入, 2=卖出
            "direction": 1,  // 必需: 1=做多, 2=做空
            "value_usd": 2150000,  // 必需: 交易价值或仓位价值
            "token": "BTC",  // 必需: 代币符号
            "trader_address": "0x1234567890abcdef1234567890abcdef12345678"  // 必需: 交易员地址
            "liquidation_price": 2980.50  // 强平时必需: 强平价格
        }

    Returns:
        {
            "success": true,
            "message": "Whale trade alert sent to multiple groups",
            "sent_count": 2,
            "failed_count": 0
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

        # 验证必需参数
        message_type = data.get('message_type')
        if message_type not in [1, 2]:
            return jsonify({
                'success': False,
                'error': 'Invalid message_type. Must be 1 (trade) or 2 (liquidation)'
            }), 400

        # 基础必需参数
        required_fields = ['direction', 'value_usd', 'token', 'trader_address']

        # 交易消息需要action
        if message_type == 1:
            required_fields.append('action')

        # 强平消息需要liquidation_price
        if message_type == 2:
            required_fields.append('liquidation_price')

        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # 验证参数值
        direction = data.get('direction')
        if direction not in [1, 2]:
            return jsonify({
                'success': False,
                'error': 'Invalid direction. Must be 1 (long) or 2 (short)'
            }), 400

        if message_type == 1:
            action = data.get('action')
            if action not in [1, 2]:
                return jsonify({
                    'success': False,
                    'error': 'Invalid action. Must be 1 (buy) or 2 (sell)'
                }), 400

        # 默认发送到两个群组（中英文各自格式）
        return send_to_both_groups(data, message_type)

    except Exception as e:
        logger.error(f"❌ Error sending whale message: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def convert_params_to_text(data: dict, language: str) -> dict:
    """
    将整数参数转换为对应语言的文本

    Args:
        data: 包含整数参数的原始数据
        language: 目标语言 'zh' 或 'en'

    Returns:
        dict: 转换后的数据
    """
    converted = data.copy()

    # 转换action (1=买入/Long, 2=卖出/Short)
    if 'action' in data and isinstance(data['action'], int):
        converted['action'] = ACTION_MAP.get(data['action'], {}).get(language, 'Long')

    # 转换direction (1=做多/Long, 2=做空/Short)
    if 'direction' in data and isinstance(data['direction'], int):
        converted['direction'] = DIRECTION_MAP.get(data['direction'], {}).get(language, 'Long')

    # 转换position_type (用于清算消息)
    if 'direction' in converted:
        # 对于清算消息，position_type和direction是一样的
        if isinstance(data.get('direction'), int):
            converted['position_type'] = POSITION_TYPE_MAP.get(data['direction'], {}).get(language, 'Long')

    return converted


def send_to_both_groups(data: dict, message_type: int) -> tuple:
    """
    发送消息到中英文两个群组

    Args:
        data: 消息数据
        message_type: 消息类型 (1=交易, 2=强平)

    Returns:
        tuple: (response, status_code)
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    results = {'success': [], 'failed': []}

    # 发送中文消息到中文群组
    zh_chat_id = settings.get_chat_id('zh')
    if zh_chat_id:
        converted_data_zh = convert_params_to_text(data, 'zh')
        try:
            if message_type == 1:
                message_zh = format_whale_trade_from_dict(converted_data_zh, language='zh')
            else:
                message_zh = format_liquidation_from_dict(converted_data_zh, language='zh')

            zh_id = int(zh_chat_id) if not zh_chat_id.startswith('@') else zh_chat_id
            success = loop.run_until_complete(
                telegram_sender.send_message(
                    chat_id=zh_id,
                    text=message_zh,
                    parse_mode='Markdown'
                )
            )
            if success:
                results['success'].append(zh_id)
                logger.info(f"✅ Message sent to Chinese group: {zh_id}")
            else:
                results['failed'].append(zh_id)
        except Exception as e:
            logger.error(f"Failed to send to Chinese group: {e}")
            results['failed'].append(zh_chat_id)

    # 发送英文消息到英文群组
    en_chat_id = settings.get_chat_id('en')
    if en_chat_id:
        converted_data_en = convert_params_to_text(data, 'en')
        try:
            if message_type == 1:
                message_en = format_whale_trade_from_dict(converted_data_en, language='en')
            else:
                message_en = format_liquidation_from_dict(converted_data_en, language='en')

            en_id = int(en_chat_id) if not en_chat_id.startswith('@') else en_chat_id
            success = loop.run_until_complete(
                telegram_sender.send_message(
                    chat_id=en_id,
                    text=message_en,
                    parse_mode='Markdown'
                )
            )
            if success:
                results['success'].append(en_id)
                logger.info(f"✅ Message sent to English group: {en_id}")
            else:
                results['failed'].append(en_id)
        except Exception as e:
            logger.error(f"Failed to send to English group: {e}")
            results['failed'].append(en_chat_id)

    msg_type_name = 'trade' if message_type == 1 else 'liquidation'
    return jsonify({
        'success': True,
        'message': f'Whale {msg_type_name} alert sent to multiple groups',
        'sent_count': len(results['success']),
        'failed_count': len(results['failed'])
    }), 200


@whale_bp.route('/trade', methods=['POST'])
def send_whale_trade():
    """
    发送巨鲸交易消息

    Body:
        {
            "action": "买入",  // "买入" 或 "卖出"（中文）; "Long" 或 "Short"（英文）
            "value_usd": 2150000,
            "token": "BTC",
            "direction": "做多 (Long)",  // "做多 (Long)" 或 "做空 (Short)"（中文）; "Long" 或 "Short"（英文）
            "trader_address": "0x1234567890abcdef1234567890abcdef12345678",
            "language": "zh"  // 可选: "zh", "en", "both"
        }

    Returns:
        {
            "success": true,
            "message": "Whale trade alert sent successfully"
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

        # 验证必需参数
        required_fields = ['action', 'value_usd', 'token', 'direction', 'trader_address']
        missing_fields = [f for f in required_fields if f not in data]

        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # 获取目标群组和语言
        language = data.get('language')
        chat_id = data.get('chat_id')

        # 处理 language='both' 的情况：分别发送中英文消息
        if not chat_id and language == 'both':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            results = {'success': [], 'failed': []}

            # 发送中文消息到中文群组
            zh_chat_id = settings.get_chat_id('zh')
            if zh_chat_id:
                message_zh = format_whale_trade_from_dict(data, language='zh')
                try:
                    zh_id = int(zh_chat_id) if not zh_chat_id.startswith('@') else zh_chat_id
                    success = loop.run_until_complete(
                        telegram_sender.send_message(
                            chat_id=zh_id,
                            text=message_zh,
                            parse_mode='Markdown'
                        )
                    )
                    if success:
                        results['success'].append(zh_id)
                        logger.info(f"✅ Whale trade sent to Chinese group: {zh_id}")
                    else:
                        results['failed'].append(zh_id)
                except Exception as e:
                    logger.error(f"Failed to send to Chinese group: {e}")
                    results['failed'].append(zh_chat_id)

            # 发送英文消息到英文群组
            en_chat_id = settings.get_chat_id('en')
            if en_chat_id:
                message_en = format_whale_trade_from_dict(data, language='en')
                try:
                    en_id = int(en_chat_id) if not en_chat_id.startswith('@') else en_chat_id
                    success = loop.run_until_complete(
                        telegram_sender.send_message(
                            chat_id=en_id,
                            text=message_en,
                            parse_mode='Markdown'
                        )
                    )
                    if success:
                        results['success'].append(en_id)
                        logger.info(f"✅ Whale trade sent to English group: {en_id}")
                    else:
                        results['failed'].append(en_id)
                except Exception as e:
                    logger.error(f"Failed to send to English group: {e}")
                    results['failed'].append(en_chat_id)

            return jsonify({
                'success': True,
                'message': 'Whale trade alert sent to multiple groups',
                'sent_count': len(results['success']),
                'failed_count': len(results['failed'])
            }), 200

        # 确定chat_id和language
        if not chat_id:
            if language:
                chat_id = settings.get_chat_id(language)
            else:
                chat_id = settings.DEFAULT_CHAT_ID
                language = 'zh'  # 默认中文
        elif not language:
            language = 'zh'  # 如果指定了chat_id但没指定language，默认中文

        if not chat_id:
            return jsonify({
                'success': False,
                'error': 'No chat_id specified'
            }), 400

        # 根据语言生成对应格式的消息
        message = format_whale_trade_from_dict(data, language=language)

        # 转换chat_id
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
            logger.info(f"✅ Whale trade alert sent to {chat_id} ({language})")
            return jsonify({
                'success': True,
                'message': 'Whale trade alert sent successfully',
                'chat_id': chat_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send message'
            }), 500

    except Exception as e:
        logger.error(f"❌ Error sending whale trade alert: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@whale_bp.route('/liquidation', methods=['POST'])
def send_liquidation():
    """
    发送清算消息

    Body:
        {
            "position_type": "做空",  // "做多" 或 "做空"（中文）; "Long" 或 "Short"（英文）
            "token": "ETH",
            "position_value": 3450000,
            "liquidation_price": 2980.50,
            "trader_address": "0x1234567890abcdef1234567890abcdef12345678",
            "language": "zh"  // 可选: "zh", "en", "both"
        }

    Returns:
        {
            "success": true,
            "message": "Liquidation alert sent successfully"
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

        # 验证必需参数
        required_fields = ['position_type', 'token', 'position_value', 'liquidation_price', 'trader_address']
        missing_fields = [f for f in required_fields if f not in data]

        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # 获取目标群组和语言
        language = data.get('language')
        chat_id = data.get('chat_id')

        # 处理 language='both' 的情况：分别发送中英文消息
        if not chat_id and language == 'both':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            results = {'success': [], 'failed': []}

            # 发送中文消息到中文群组
            zh_chat_id = settings.get_chat_id('zh')
            if zh_chat_id:
                message_zh = format_liquidation_from_dict(data, language='zh')
                try:
                    zh_id = int(zh_chat_id) if not zh_chat_id.startswith('@') else zh_chat_id
                    success = loop.run_until_complete(
                        telegram_sender.send_message(
                            chat_id=zh_id,
                            text=message_zh,
                            parse_mode='Markdown'
                        )
                    )
                    if success:
                        results['success'].append(zh_id)
                        logger.info(f"✅ Liquidation alert sent to Chinese group: {zh_id}")
                    else:
                        results['failed'].append(zh_id)
                except Exception as e:
                    logger.error(f"Failed to send to Chinese group: {e}")
                    results['failed'].append(zh_chat_id)

            # 发送英文消息到英文群组
            en_chat_id = settings.get_chat_id('en')
            if en_chat_id:
                message_en = format_liquidation_from_dict(data, language='en')
                try:
                    en_id = int(en_chat_id) if not en_chat_id.startswith('@') else en_chat_id
                    success = loop.run_until_complete(
                        telegram_sender.send_message(
                            chat_id=en_id,
                            text=message_en,
                            parse_mode='Markdown'
                        )
                    )
                    if success:
                        results['success'].append(en_id)
                        logger.info(f"✅ Liquidation alert sent to English group: {en_id}")
                    else:
                        results['failed'].append(en_id)
                except Exception as e:
                    logger.error(f"Failed to send to English group: {e}")
                    results['failed'].append(en_chat_id)

            return jsonify({
                'success': True,
                'message': 'Liquidation alert sent to multiple groups',
                'sent_count': len(results['success']),
                'failed_count': len(results['failed'])
            }), 200

        # 确定chat_id和language
        if not chat_id:
            if language:
                chat_id = settings.get_chat_id(language)
            else:
                chat_id = settings.DEFAULT_CHAT_ID
                language = 'zh'  # 默认中文
        elif not language:
            language = 'zh'  # 如果指定了chat_id但没指定language，默认中文

        if not chat_id:
            return jsonify({
                'success': False,
                'error': 'No chat_id specified'
            }), 400

        # 根据语言生成对应格式的消息
        message = format_liquidation_from_dict(data, language=language)

        # 转换chat_id
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
            logger.info(f"✅ Liquidation alert sent to {chat_id} ({language})")
            return jsonify({
                'success': True,
                'message': 'Liquidation alert sent successfully',
                'chat_id': chat_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send message'
            }), 500

    except Exception as e:
        logger.error(f"❌ Error sending liquidation alert: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
