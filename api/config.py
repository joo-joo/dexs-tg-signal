"""
配置模块
管理所有配置项
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """应用配置"""

    # Telegram配置
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')

    # 多群组配置
    CHAT_ID_ZH: str = os.getenv('CHAT_ID_ZH', '')  # 中文群组
    CHAT_ID_EN: str = os.getenv('CHAT_ID_EN', '')  # 英文群组
    DEFAULT_CHAT_ID: str = os.getenv('CHAT_ID', os.getenv('CHAT_ID_ZH', ''))  # 默认使用中文群组

    # API服务器配置
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', 5001))
    API_DEBUG: bool = os.getenv('API_DEBUG', 'False').lower() == 'true'

    # 日志配置
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    # Telegram消息配置
    MESSAGE_PARSE_MODE: str = 'Markdown'
    MESSAGE_RETRY_COUNT: int = 3
    MESSAGE_RETRY_DELAY: float = 1.0
    MESSAGE_BATCH_DELAY: float = 0.1

    def __init__(self):
        """验证配置"""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required in .env file")

    def get_telegram_config(self) -> dict:
        """获取Telegram配置"""
        return {
            'bot_token': self.BOT_TOKEN,
            'default_chat_id': self.DEFAULT_CHAT_ID,
            'chat_id_zh': self.CHAT_ID_ZH,
            'chat_id_en': self.CHAT_ID_EN,
            'parse_mode': self.MESSAGE_PARSE_MODE,
            'retry_count': self.MESSAGE_RETRY_COUNT,
            'retry_delay': self.MESSAGE_RETRY_DELAY,
        }

    def get_api_config(self) -> dict:
        """获取API配置"""
        return {
            'host': self.API_HOST,
            'port': self.API_PORT,
            'debug': self.API_DEBUG,
        }

    def get_chat_id(self, language: str = None) -> str:
        """
        获取群组ID

        Args:
            language: 语言代码 ('zh', 'en', 'both')，None使用默认

        Returns:
            str: 群组ID或逗号分隔的多个ID
        """
        if language == 'zh':
            return self.CHAT_ID_ZH
        elif language == 'en':
            return self.CHAT_ID_EN
        elif language == 'both':
            return f"{self.CHAT_ID_ZH},{self.CHAT_ID_EN}"
        else:
            return self.DEFAULT_CHAT_ID

    def get_all_chat_ids(self) -> list:
        """获取所有群组ID列表"""
        chat_ids = []
        if self.CHAT_ID_ZH:
            try:
                chat_ids.append(int(self.CHAT_ID_ZH))
            except ValueError:
                pass
        if self.CHAT_ID_EN:
            try:
                chat_ids.append(int(self.CHAT_ID_EN))
            except ValueError:
                pass
        return chat_ids


# 全局配置实例
settings = Settings()
