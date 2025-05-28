# 配置文件
import os
from passlib.context import CryptContext

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 管理员密码配置
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # 可以通过环境变量设置

# PicGo 图床配置
PICGO_API_URL = "https://www.picgo.net/api/1/upload"
PICGO_API_KEY = "chv_S0DhK_bc5877cd95324f9765378583d06860a94de167f1ba53acea46d9222c7710690062cf6bbc81ae58aabfe71240dc0ea4a6875f7f8fca5bf16520f039f6b816420d"

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
