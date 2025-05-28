from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from datetime import datetime

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # 如果没有环境变量，使用默认配置
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
    DB_NAME = os.getenv("DB_NAME", "meme_db")
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 创建SQLAlchemy引擎和会话
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 图片模型定义
class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_name = Column(String(255), unique=True, index=True)  # 文件名，包含扩展名
    file_hash = Column(String(32), unique=True, index=True)   # 图片的MD5哈希值
    file_path = Column(String(255))                           # 本地图片存储路径（可选）
    image_bed_url = Column(String(500))                       # 图床URL（主要获取图片的地址）
    is_checked = Column(Boolean, default=False)               # 是否已审核
    likes = Column(Integer, default=0)                        # 点赞数
    dislikes = Column(Integer, default=0)                     # 点踩数    upload_time = Column(DateTime, default=datetime.now)      # 上传时间
    file_size = Column(Integer)                               # 文件大小（字节）
    mime_type = Column(String(50))                            # MIME类型
    width = Column(Integer, default=0)                        # 图片宽度（像素）
    height = Column(Integer, default=0)                       # 图片高度（像素）

# 创建数据库表
def create_tables():
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 添加新图片到数据库
def add_image(db: Session, file_name: str, file_hash: str, file_path: str,
              image_bed_url: str, is_checked: bool, file_size: int, mime_type: str,
              width: int, height: int):
    db_image = Image(
        file_name=file_name,
        file_hash=file_hash,
        file_path=file_path,
        image_bed_url=image_bed_url,
        is_checked=is_checked,
        file_size=file_size,
        mime_type=mime_type,
        width=width,
        height=height
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

# 根据哈希值查询图片
def get_image_by_hash(db: Session, file_hash: str):
    return db.query(Image).filter(Image.file_hash == file_hash).first()

# 根据ID获取图片
def get_image_by_id(db: Session, image_id: int):
    return db.query(Image).filter(Image.id == image_id).first()

# 根据文件名获取图片
def get_image_by_filename(db: Session, filename: str):
    return db.query(Image).filter(Image.file_name == filename).first()

# 获取随机一张已审核的图片，可以排除当前图片
def get_random_checked_image(db: Session, current_id: int = None):
    query = db.query(Image).filter(Image.is_checked == True)
    
    # 如果提供了当前图片ID，排除它
    if current_id:
        query = query.filter(Image.id != current_id)
    
    # 使用数据库随机函数选择一张图片
    # 注意：不同数据库的随机函数可能不同，这里使用MySQL的RAND()
    return query.order_by(func.rand()).first()

# 获取所有已审核的图片
def get_all_checked_images(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Image).filter(Image.is_checked == True).offset(skip).limit(limit).all()

# 获取所有未审核的图片
def get_all_unchecked_images(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Image).filter(Image.is_checked == False).offset(skip).limit(limit).all()

# 更新图片状态为已审核
def update_image_checked_status(db: Session, image_id: int, is_checked: bool):
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if db_image:
        db_image.is_checked = is_checked
        db.commit()
        db.refresh(db_image)
        return db_image
    return None

# 更新图片点赞数
def update_image_likes(db: Session, image_id: int, increment: bool = True):
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if db_image:
        if increment:
            db_image.likes += 1
        else:
            # 防止点赞数变成负数
            db_image.likes = max(0, db_image.likes - 1)
        db.commit()
        db.refresh(db_image)
        return db_image
    return None

# 更新图片点踩数
def update_image_dislikes(db: Session, image_id: int, increment: bool = True):
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if db_image:
        if increment:
            db_image.dislikes += 1
        else:
            # 防止点踩数变成负数
            db_image.dislikes = max(0, db_image.dislikes - 1)
        db.commit()
        db.refresh(db_image)
        return db_image
    return None