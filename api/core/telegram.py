"""
Telegram核心模块
封装Telegram Bot功能
"""
import asyncio
import logging
from typing import Optional, Union, List
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class TelegramSender:
    """
    Telegram消息发送器
    """

    def __init__(self, bot_token: str):
        """
        初始化Telegram发送器

        Args:
            bot_token: Telegram Bot Token
        """
        self.bot = Bot(token=bot_token)
        self._initialized = False
        logger.info("TelegramSender initialized")

    async def initialize(self):
        """初始化Bot连接"""
        try:
            bot_info = await self.bot.get_me()
            self._initialized = True
            logger.info(f"✅ Bot connected: @{bot_info.username}")
            return True
        except Exception as e:
            logger.error(f"❌ Bot initialization failed: {e}")
            return False

    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: Optional[str] = 'Markdown',
        disable_web_page_preview: bool = True,
        retry_count: int = 3,
        retry_delay: float = 1.0
    ) -> bool:
        """
        发送消息到指定的群组/频道

        Args:
            chat_id: 目标群组ID或频道用户名
            text: 消息文本
            parse_mode: 解析模式
            disable_web_page_preview: 是否禁用网页预览
            retry_count: 失败重试次数
            retry_delay: 重试延迟（秒）

        Returns:
            bool: 发送是否成功
        """
        if not self._initialized:
            logger.warning("Bot not initialized, attempting to initialize...")
            if not await self.initialize():
                return False

        for attempt in range(retry_count):
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode=parse_mode,
                    disable_web_page_preview=disable_web_page_preview
                )
                logger.info(f"✅ Message sent to chat {chat_id}")
                return True

            except TelegramError as e:
                logger.error(f"❌ Send failed (attempt {attempt + 1}/{retry_count}): {e}")

                # 某些错误不需要重试
                if "chat not found" in str(e).lower():
                    logger.error("Chat not found, stopping retry")
                    return False
                elif "bot was blocked" in str(e).lower():
                    logger.error("Bot was blocked, stopping retry")
                    return False

                # 如果还有重试机会，等待后重试
                if attempt < retry_count - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))

            except Exception as e:
                logger.error(f"❌ Unknown error: {e}")
                return False

        return False

    async def send_to_multiple_chats(
        self,
        chat_ids: List[Union[int, str]],
        text: str,
        parse_mode: Optional[str] = 'Markdown',
        disable_web_page_preview: bool = True,
        delay_between_sends: float = 0.1
    ) -> dict:
        """
        向多个群组/频道发送相同消息

        Args:
            chat_ids: 目标群组ID列表
            text: 消息文本
            parse_mode: 解析模式
            disable_web_page_preview: 是否禁用网页预览
            delay_between_sends: 每次发送间隔（秒）

        Returns:
            dict: {'success': [成功的chat_id列表], 'failed': [失败的chat_id列表]}
        """
        success = []
        failed = []

        for chat_id in chat_ids:
            result = await self.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview
            )

            if result:
                success.append(chat_id)
            else:
                failed.append(chat_id)

            # 添加延迟避免限流
            if delay_between_sends > 0:
                await asyncio.sleep(delay_between_sends)

        logger.info(f"📤 Batch send completed - success: {len(success)}, failed: {len(failed)}")
        return {'success': success, 'failed': failed}

    async def close(self):
        """关闭Bot连接"""
        try:
            await self.bot.shutdown()
            logger.info("✅ Bot connection closed")
        except AttributeError:
            pass
        except Exception as e:
            logger.error(f"❌ Failed to close Bot: {e}")
