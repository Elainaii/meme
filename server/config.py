# 项目配置文件 - 包含所有配置常量和环境变量设置
import os
import secrets
from os import abort
from pathlib import Path
from passlib.context import CryptContext

# 自动加载 .env 文件

from dotenv import load_dotenv
# 查找 .env 文件的路径
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"已加载 .env 文件: {env_path}")
else:
    print(f"未找到 .env 文件: {env_path}")
    abort()


# ========== JWT配置 ==========
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# ========== 管理员配置 ==========
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # 请通过环境变量设置安全密码

# ========== 图床配置 ==========
PICGO_API_URL = os.getenv("PICGO_API_URL", "https://www.picgo.net/api/1/upload")
PICGO_API_KEY = os.getenv("PICGO_API_KEY", "")  # 请在环境变量中设置您的PicGo API密钥

# ========== 服务器配置 ==========
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

# ========== 数据库配置 ==========
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")  # 请设置数据库密码
    DB_NAME = os.getenv("DB_NAME", "meme_db")
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ========== 文件路径配置 ==========
# 定义根目录路径和图片目录路径
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# 图片存储在根目录的images文件夹下
IMAGES_DIR = os.path.join(ROOT_DIR, "images")
CHECKED_DIR = os.path.join(IMAGES_DIR, "checked")
UNCHECKED_DIR = os.path.join(IMAGES_DIR, "unchecked")

# 示例图片路径
EXAMPLE_IMAGE_PATH = os.path.join(IMAGES_DIR, "example.jpg")

# ========== 文件上传配置 ==========
# 允许的文件类型
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]

# 文件大小限制（字节）
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 默认10MB

# ========== 分页配置 ==========
DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "100"))

# ========== CORS 配置 ==========
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://localhost:3002",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001", 
    "http://127.0.0.1:8000",
]

# 生产环境可以通过环境变量添加更多源
ADDITIONAL_CORS_ORIGINS = os.getenv("ADDITIONAL_CORS_ORIGINS", "")
if ADDITIONAL_CORS_ORIGINS:
    CORS_ORIGINS.extend([origin.strip() for origin in ADDITIONAL_CORS_ORIGINS.split(",")])

# ========== API 配置 ==========
API_V1_PREFIX = "/api/v1"
API_TITLE = "Meme API"
API_DESCRIPTION = "Meme图片管理API"
API_VERSION = "1.0.0"

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """生成密码哈希"""
    return pwd_context.hash(password)

def verify_admin_password(password: str) -> bool:
    """验证管理员密码"""
    return password == ADMIN_PASSWORD
