"""
健康检查路由
"""
from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

# Telegram发送器实例
telegram_sender = None


def set_telegram_sender(sender):
    """设置Telegram发送器实例"""
    global telegram_sender
    telegram_sender = sender


@health_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'service': 'telegram-sender',
        'version': '1.0.0',
        'telegram_ready': telegram_sender is not None
    }), 200


@health_bp.route('/ping', methods=['GET'])
def ping():
    """简单的ping接口"""
    return jsonify({'message': 'pong'}), 200
