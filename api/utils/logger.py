"""
日志配置模块
"""
import logging
import sys
from api.config import settings

# 配置日志格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 配置根日志记录器
logging.basicConfig(
    format=log_format,
    level=getattr(logging, settings.LOG_LEVEL),
    stream=sys.stdout
)

# 创建应用日志记录器
logger = logging.getLogger('telegram_api')

# 配置httpx日志级别（避免太多HTTP日志）
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)
