"""
Telegram Signal API - 主启动文件

提供HTTP API接口用于发送Telegram消息

使用方法:
    python main.py

API文档: http://localhost:5001/health
"""
import asyncio
from flask import Flask
from api.config import settings
from api.core.telegram import TelegramSender
from api.routers import health, message, whale
from api.utils.logger import logger


def create_app() -> Flask:
    """
    创建Flask应用

    Returns:
        Flask: Flask应用实例
    """
    app = Flask(__name__)

    # 注册蓝图
    app.register_blueprint(health.health_bp)
    app.register_blueprint(message.message_bp)
    app.register_blueprint(whale.whale_bp)

    logger.info("✅ Flask app created")
    return app


def init_telegram() -> TelegramSender:
    """
    初始化Telegram发送器

    Returns:
        TelegramSender: Telegram发送器实例

    Raises:
        RuntimeError: 初始化失败时抛出
    """
    try:
        sender = TelegramSender(bot_token=settings.BOT_TOKEN)

        # 在新的event loop中初始化
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(sender.initialize())

        if not success:
            raise RuntimeError("Failed to initialize Telegram Bot")

        logger.info("✅ Telegram sender initialized")
        return sender

    except Exception as e:
        logger.error(f"❌ Telegram initialization failed: {e}")
        raise


def main():
    """主函数"""
    try:
        # 打印启动信息
        logger.info("=" * 60)
        logger.info("🚀 Starting Telegram Signal API")
        logger.info("=" * 60)

        # 初始化Telegram发送器
        telegram_sender = init_telegram()

        # 设置Telegram发送器到路由
        health.set_telegram_sender(telegram_sender)
        message.set_telegram_sender(telegram_sender)
        whale.set_telegram_sender(telegram_sender)

        # 创建Flask应用
        app = create_app()

        # 获取API配置
        api_config = settings.get_api_config()
        host = api_config['host']
        port = api_config['port']
        debug = api_config['debug']

        # 打印API信息
        logger.info("=" * 60)
        logger.info(f"🌐 API Server: http://{host}:{port}")
        logger.info("=" * 60)
        logger.info("📝 Available Endpoints:")
        logger.info(f"  • GET  /health              - Health check")
        logger.info(f"  • GET  /ping                - Ping")
        logger.info(f"  • POST /api/v1/send         - Send message")
        logger.info(f"  • POST /api/v1/send/multiple - Batch send")
        logger.info(f"  • POST /api/v1/send/formatted - Send formatted message")
        logger.info(f"  • POST /api/v1/whale/send   - Send whale message (unified)")
        logger.info(f"  • POST /api/v1/whale/trade  - Send whale trade alert")
        logger.info(f"  • POST /api/v1/whale/liquidation - Send liquidation alert")
        logger.info("=" * 60)
        logger.info("💡 Press CTRL+C to stop")
        logger.info("=" * 60)

        # 启动Flask服务器
        app.run(host=host, port=port, debug=debug)

    except KeyboardInterrupt:
        logger.info("\n⚠️  Received interrupt signal")
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}", exc_info=True)
        exit(1)
    finally:
        logger.info("=" * 60)
        logger.info("🔚 Server stopped")
        logger.info("=" * 60)


if __name__ == '__main__':
    main()
