# 图片处理工具
import hashlib
import os
import shutil
from io import BytesIO
from PIL import Image as PILImage
from typing import Tuple

# 导入日志
from logger_config import get_logger

from config import EXAMPLE_IMAGE_PATH, IMAGES_DIR

logger = get_logger(__name__)


def get_image_dimensions(image_content: bytes) -> Tuple[int, int]:
    """从图片二进制数据获取宽度和高度"""
    try:
        with PILImage.open(BytesIO(image_content)) as img:
            return img.size  # 返回 (width, height)
    except Exception as e:
        logger.error(f"获取图片尺寸失败: {e}")
        return (0, 0)


def calculate_file_hash(content: bytes) -> str:
    """计算文件的MD5哈希值"""
    return hashlib.md5(content).hexdigest()


def create_safe_filename(filename: str, file_hash: str = "") -> str:
    """创建安全的文件名"""
    if not filename:
        return f"{file_hash}.jpg" if file_hash else "image.jpg"
    
    # 确保文件名安全
    safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    if not safe_filename:
        safe_filename = f"{file_hash}.jpg" if file_hash else "image.jpg"
    
    return safe_filename


def get_unique_filepath(base_path: str) -> str:
    """如果文件已存在，添加数字后缀获取唯一路径"""
    if not os.path.exists(base_path):
        return base_path
    
    counter = 1
    name, ext = os.path.splitext(base_path)
    while True:
        new_path = f"{name}_{counter}{ext}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def ensure_directories():
    """确保必要的目录存在"""
    from config import CHECKED_DIR, UNCHECKED_DIR
    os.makedirs(CHECKED_DIR, exist_ok=True)
    os.makedirs(UNCHECKED_DIR, exist_ok=True)


def setup_example_image():
    """设置示例图片"""
    if not os.path.exists(EXAMPLE_IMAGE_PATH):
        SERVER_EXAMPLE = os.path.join(os.path.dirname(__file__), "..", "images", "example.jpg")
        if os.path.exists(SERVER_EXAMPLE):
            # 如果服务器目录下有示例图片，复制到根目录
            shutil.copy(SERVER_EXAMPLE, EXAMPLE_IMAGE_PATH)
            logger.info(f"已复制示例图片到: {EXAMPLE_IMAGE_PATH}")
        else:
            logger.warning("警告: 未找到示例图片")


def validate_image_type(content_type: str) -> bool:
    """验证图片类型是否允许"""
    from config import ALLOWED_IMAGE_TYPES
    return content_type in ALLOWED_IMAGE_TYPES
