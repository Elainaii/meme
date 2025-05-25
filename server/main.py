from fastapi import FastAPI, File, Response, UploadFile, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import shutil
import hashlib
from typing import List, Optional
import glob
from datetime import timedelta

# 导入数据库相关模块
from .database import (
    get_db, Image, create_tables, add_image, get_image_by_hash,
    get_image_by_id, get_image_by_filename, get_random_checked_image,
    get_all_checked_images, get_all_unchecked_images,
    update_image_checked_status, update_image_likes, update_image_dislikes
)

# 导入认证相关模块
from .config import verify_admin_password, ACCESS_TOKEN_EXPIRE_MINUTES
from .auth import create_access_token, get_current_admin_user

app = FastAPI()

# 在应用启动时创建数据库表并执行迁移
@app.on_event("startup")
async def startup_db_client():
    create_tables()

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义根目录路径和图片目录路径
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# 图片存储在根目录的images文件夹下
IMAGES_DIR = os.path.join(ROOT_DIR, "images")
CHECKED_DIR = os.path.join(IMAGES_DIR, "checked")
UNCHECKED_DIR = os.path.join(IMAGES_DIR, "unchecked")

# 确保图片目录存在
os.makedirs(CHECKED_DIR, exist_ok=True)
os.makedirs(UNCHECKED_DIR, exist_ok=True)

# 示例图片路径 - 如果根目录下没有，则使用服务器目录下的备用图片
EXAMPLE_IMAGE_PATH = os.path.join(IMAGES_DIR, "example.jpg")
if not os.path.exists(EXAMPLE_IMAGE_PATH):
    SERVER_EXAMPLE = os.path.join(os.path.dirname(__file__), "images", "example.jpg")
    if os.path.exists(SERVER_EXAMPLE):
        # 如果服务器目录下有示例图片，复制到根目录
        shutil.copy(SERVER_EXAMPLE, EXAMPLE_IMAGE_PATH)
    else:
        print("警告: 未找到示例图片")

# 定义图片信息响应模型
class ImageInfo(BaseModel):
    id: int
    file_name: str
    is_checked: bool
    likes: int
    dislikes: int
    
    class Config:
        from_attributes = True

# 定义请求和响应模型
class AdminLoginRequest(BaseModel):
    password: str

class AdminLoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None

class AdminImageResponse(BaseModel):
    id: int
    file_name: str
    is_checked: bool
    likes: int
    dislikes: int
    file_size: int
    created_at: str


@app.get("/image")
async def fetch_random_image(current: str = "", db: Session = Depends(get_db)):
    """从数据库随机获取一张已审核的图片，可以指定当前图片以获取不同的图片"""
    current_id = None

    # 如果提供了当前图片名称，获取其ID
    if current:
        current_image = db.query(Image).filter(Image.file_name == current).first()
        if current_image:
            current_id = current_image.id
    
    # 从数据库获取随机图片
    db_image = get_random_checked_image(db, current_id)
      # 如果数据库中没有已审核的图片，则使用示例图片
    if not db_image:
        with open(EXAMPLE_IMAGE_PATH, "rb") as image_file:
            content = image_file.read()
        return Response(content=content, media_type="image/jpeg")
    
    # 构建图片路径并读取文件
    image_path = db_image.file_path
      # 确保文件存在
    if not os.path.exists(image_path):
        with open(EXAMPLE_IMAGE_PATH, "rb") as image_file:
            content = image_file.read()
        return Response(content=content, media_type="image/jpeg")
    
    # 读取文件内容
    with open(image_path, "rb") as image_file:
        content = image_file.read()
    
    # 使用数据库中存储的媒体类型
    media_type = db_image.mime_type
    
    # 添加图片信息到响应头
    headers = {
        "X-Image-Name": db_image.file_name,
        "X-Image-ID": str(db_image.id),
        "X-Image-Likes": str(db_image.likes),
        "X-Image-Dislikes": str(db_image.dislikes)
    }
    
    return Response(content=content, media_type=media_type, headers=headers)

@app.get("/image/checked/{image_id}")
async def fetch_checked_image(image_id: int, db: Session = Depends(get_db)):
    """从数据库中获取指定ID的已审核图片"""
    db_image = db.query(Image).filter(Image.id == image_id, Image.is_checked == True).first()

    if not db_image:
        raise HTTPException(status_code=404, detail="未找到该ID的审核图片")
    
    image_path = db_image.file_path
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="图片文件不存在")
    
    with open(image_path, "rb") as image_file:
        content = image_file.read()
    
    # 使用数据库中存储的媒体类型
    media_type = db_image.mime_type
    
    # 添加图片信息到响应头
    headers = {
        "X-Image-Name": db_image.file_name,
        "X-Image-ID": str(db_image.id),
        "X-Image-Likes": str(db_image.likes),
        "X-Image-Dislikes": str(db_image.dislikes)
    }
    
    return Response(content=content, media_type=media_type, headers=headers)


@app.get("/image/unchecked/{image_id}")
async def fetch_unchecked_image(image_id: int, db: Session = Depends(get_db)):
    """从数据库中获取指定ID的未审核图片"""
    db_image = db.query(Image).filter(Image.id == image_id, Image.is_checked == False).first()
    
    if not db_image:
        raise HTTPException(status_code=404, detail="未找到该ID的未审核图片")
    
    image_path = db_image.file_path
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="图片文件不存在")
    
    with open(image_path, "rb") as image_file:
        content = image_file.read()
    
    # 使用数据库中存储的媒体类型
    media_type = db_image.mime_type
    
    # 添加图片信息到响应头
    headers = {
        "X-Image-Name": db_image.file_name,
        "X-Image-ID": str(db_image.id)
    }
    
    return Response(content=content, media_type=media_type, headers=headers)

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """上传图片并将信息存入数据库"""
    # 检查文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="只允许上传图片文件（JPEG, PNG, GIF）"
        )
    
    # 获取文件扩展名
    file_ext = os.path.splitext(file.filename)[1]
    
    # 读取文件内容并计算哈希值用于查重
    contents = await file.read()
    file_hash = hashlib.md5(contents).hexdigest()
      # 重置文件指针
    await file.seek(0)
    
    # 检查数据库中是否已存在相同哈希值的图片
    existing_image = get_image_by_hash(db, file_hash)
    
    if existing_image:
        # 将绝对路径转换为相对路径（如果需要）
        if os.path.isabs(existing_image.file_path):
            # 检查是否是以前的绝对路径格式
            filename = os.path.basename(existing_image.file_path)
            if existing_image.is_checked:
                new_path = os.path.join(CHECKED_DIR, filename)
            else:
                new_path = os.path.join(UNCHECKED_DIR, filename)
            # 更新数据库中的路径
            existing_image.file_path = new_path
            db.commit()
            
        # 确保文件确实存在于文件系统中
        if not os.path.exists(existing_image.file_path):
            # 如果数据库有记录但文件不存在，则保存文件
            # 确保目录存在
            os.makedirs(os.path.dirname(existing_image.file_path), exist_ok=True)
            with open(existing_image.file_path, "wb") as buffer:
                await file.seek(0)
                shutil.copyfileobj(file.file, buffer)
        
        return {
            "status": "success", 
            "message": "图片已存在",
            "filename": existing_image.file_name,
            "id": existing_image.id,
            "path": existing_image.file_path
        }    # 构建新文件名和路径，默认为未审核状态
    new_filename = f"{file_hash}{file_ext}"
    # 使用相对路径 images/unchecked
    file_path = os.path.join(UNCHECKED_DIR, new_filename)
    
    # 确保目录存在（之前已经创建，这里为了保险再确认一次）
    os.makedirs(UNCHECKED_DIR, exist_ok=True)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 获取文件大小
    file_size = os.path.getsize(file_path)
    
    # 添加到数据库
    db_image = add_image(
        db=db,
        file_name=new_filename,
        file_hash=file_hash,
        file_path=file_path,
        is_checked=False,  # 默认为未审核
        file_size=file_size,
        mime_type=file.content_type
    )
    
    return {
        "status": "success", 
        "message": "图片上传成功", 
        "filename": new_filename,
        "id": db_image.id,
        "path": file_path,
        "is_checked": db_image.is_checked,
        "likes": db_image.likes,
        "dislikes": db_image.dislikes
    }

@app.post("/image/{image_id}/like")
async def like_image(image_id: int, db: Session = Depends(get_db)):
    """为指定ID的图片增加点赞数"""
    db_image = update_image_likes(db, image_id, increment=True)
    if not db_image:
        raise HTTPException(status_code=404, detail="图片未找到")
    
    return {
        "id": db_image.id,
        "likes": db_image.likes,
        "dislikes": db_image.dislikes
    }


@app.post("/image/{image_id}/dislike")
async def dislike_image(image_id: int, db: Session = Depends(get_db)):
    """为指定ID的图片增加点踩数"""
    db_image = update_image_dislikes(db, image_id, increment=True)
    if not db_image:
        raise HTTPException(status_code=404, detail="图片未找到")
    
    return {
        "id": db_image.id,
        "likes": db_image.likes,
        "dislikes": db_image.dislikes
    }


@app.get("/images/list")
async def list_images(
    checked: bool = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取图片列表，可以按照审核状态过滤"""
    if checked is not None:
        if checked:
            images = get_all_checked_images(db, skip, limit)
        else:
            images = get_all_unchecked_images(db, skip, limit)
    else:
        # 不过滤，获取所有图片
        images = db.query(Image).offset(skip).limit(limit).all()
    
    return [
        ImageInfo(
            id=img.id,
            file_name=img.file_name,
            is_checked=img.is_checked,
            likes=img.likes,
            dislikes=img.dislikes
        ) for img in images
    ]


@app.post("/image/{image_id}/check")
async def check_image(
    image_id: int,
    is_checked: bool = True,
    db: Session = Depends(get_db)
):
    """更新图片的审核状态"""
    db_image = update_image_checked_status(db, image_id, is_checked)
    if not db_image:
        raise HTTPException(status_code=404, detail="图片未找到")    # 如果审核状态改变，则需要移动文件位置
    old_path = db_image.file_path
    
    # 根据审核状态确定图片应该存放的目录
    if is_checked:
        new_dir = CHECKED_DIR  # images/checked
    else:
        new_dir = UNCHECKED_DIR  # images/unchecked
    
    # 确保目录存在
    os.makedirs(new_dir, exist_ok=True)
    
    # 构建新路径
    new_path = os.path.join(new_dir, db_image.file_name)
    
    # 如果文件路径不同，需要移动文件
    if old_path != new_path:
        if os.path.exists(old_path):
            # 先确保目标路径不存在文件
            if os.path.exists(new_path):
                os.remove(new_path)
            # 移动文件
            shutil.move(old_path, new_path)
            # 更新数据库中的文件路径
            db_image.file_path = new_path
            db.commit()
    
    return {
        "id": db_image.id,
        "file_name": db_image.file_name,
        "is_checked": db_image.is_checked,
        "file_path": db_image.file_path,
        "likes": db_image.likes,
        "dislikes": db_image.dislikes
    }


# 管理员登录API
@app.post("/admin/verify", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest):
    """管理员登录验证"""
    if verify_admin_password(request.password):
        # 创建访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": "admin"}, expires_delta=access_token_expires
        )
        return AdminLoginResponse(
            success=True,
            message="登录成功",
            token=access_token
        )
    else:
        return AdminLoginResponse(
            success=False,
            message="密码不正确"
        )

# 获取待审核图片列表（最多5张）
@app.get("/admin/pending-images")
async def get_pending_images(
    current_admin: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取待审核的图片（最多5张）"""
    try:
        print(f"Admin user: {current_admin}")
        images = get_all_unchecked_images(db, skip=0, limit=5)
        print(f"Found {len(images)} unchecked images")
        
        # 获取总数
        total = db.query(Image).filter(Image.is_checked == False).count()
        print(f"Total unchecked images: {total}")
        
        result = {
            "images": [
                {
                    "id": img.id,
                    "file_name": img.file_name,
                    "is_checked": img.is_checked,
                    "likes": img.likes,
                    "dislikes": img.dislikes,
                    "file_size": img.file_size,
                    "created_at": img.upload_time.isoformat() if img.upload_time else None
                } for img in images
            ],
            "total": total,
            "returned": len(images)
        }
        print(f"Returning result: {result}")
        return result
    except Exception as e:
        print(f"Error in get_pending_images: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# 获取已审核图片列表（分页）
@app.get("/admin/checked-images")
async def get_checked_images(
    page: int = 1,
    page_size: int = 5,
    current_admin: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取已审核图片列表（分页）"""
    skip = (page - 1) * page_size
    images = get_all_checked_images(db, skip=skip, limit=page_size)
    
    # 获取总数
    total = db.query(Image).filter(Image.is_checked == True).count()
    total_pages = (total + page_size - 1) // page_size
    return {
        "images": [
            {
                "id": img.id,
                "file_name": img.file_name,
                "is_checked": img.is_checked,
                "likes": img.likes,
                "dislikes": img.dislikes,
                "file_size": img.file_size,
                "created_at": img.upload_time.isoformat() if img.upload_time else None
            } for img in images
        ],
        "total": total,
        "current_page": page,
        "total_pages": total_pages,
        "page_size": page_size
    }

# 管理员审核图片
@app.post("/admin/review-image/{image_id}")
async def review_image(
    image_id: int,
    action: str,  # "approve" 或 "reject"
    current_admin: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """管理员审核图片"""
    if action not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="无效的操作，只支持 'approve' 或 'reject'")
    
    if action == "approve":
        # 批准图片
        result = update_image_checked_status(db, image_id, True)
        if not result:
            raise HTTPException(status_code=404, detail="图片未找到")
        
        return {"message": "图片已批准", "action": "approved"}
    
    elif action == "reject":
        # 拒绝图片（删除）
        db_image = db.query(Image).filter(Image.id == image_id).first()
        if not db_image:
            raise HTTPException(status_code=404, detail="图片未找到")
        
        # 删除文件
        if os.path.exists(db_image.file_path):
            os.remove(db_image.file_path)
        
        # 删除数据库记录
        db.delete(db_image)
        db.commit()
        
        return {"message": "图片已拒绝并删除", "action": "rejected"}

# 删除已审核图片
@app.delete("/admin/image/{image_id}")
async def delete_image(
    image_id: int,
    current_admin: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """删除指定图片"""
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if not db_image:
        raise HTTPException(status_code=404, detail="图片未找到")
    
    # 删除文件
    if os.path.exists(db_image.file_path):
        os.remove(db_image.file_path)
    
    # 删除数据库记录
    db.delete(db_image)
    db.commit()
    
    return {"message": "图片已删除", "id": image_id}

