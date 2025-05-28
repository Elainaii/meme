from fastapi import FastAPI, File, Response, UploadFile, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import shutil
import hashlib
from typing import List, Optional
from datetime import timedelta
import time
import httpx
from io import BytesIO

# 导入数据库相关模块
from database import (
    get_db, Image, create_tables, add_image, get_image_by_hash,
    get_random_checked_image, get_all_checked_images, get_all_unchecked_images,
    update_image_checked_status, update_image_likes, update_image_dislikes
)

# 导入认证相关模块
from config import (
    verify_admin_password, ACCESS_TOKEN_EXPIRE_MINUTES,
    PICGO_API_URL, PICGO_API_KEY
)
from auth import create_access_token, get_current_admin_user

app = FastAPI(title="Meme API", description="Meme图片管理API", version="1.0.0")


# 在应用启动时创建数据库表并执行迁移
@app.on_event("startup")
async def startup_db_client():
    create_tables()


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点，用于监控服务状态"""
    try:
        # 检查数据库连接
        db = next(get_db())
        # 简单地尝试获取数据库会话
        db.close()
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "database": "connected",
            "service": "running"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail={
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e)
        })

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，这样可以确保CORS不会阻止请求
    allow_credentials=False,  # 当使用通配符时必须设置为False
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


@app.get("/image-info")
async def get_image_info(current: str = "", db: Session = Depends(get_db)):
    """获取图片信息，返回图片URL而不是二进制数据"""
    current_id = None

    if current:
        current_image = db.query(Image).filter(Image.file_name == current).first()
        if current_image:
            current_id = current_image.id

    db_image = get_random_checked_image(db, current_id)

    if not db_image:
        raise HTTPException(status_code=404, detail="没有可用的图片")

    # 返回图片信息，包括图床URL
    return {
        "id": db_image.id,
        "file_name": db_image.file_name,
        "image_url": db_image.image_bed_url if db_image.image_bed_url else None,
        "likes": db_image.likes,
        "dislikes": db_image.dislikes
    }


@app.get("/test-cors")
async def test_cors():
    """测试CORS端点"""
    return {"message": "CORS正常工作", "status": "success"}


@app.get("/image")
async def fetch_random_image(current: str = "", db: Session = Depends(get_db)):
    """从数据库随机获取一张已审核的图片，返回图片信息和图床URL"""
    import time

    # 开始计时
    start_time = time.time()
    current_id = None

    # 如果提供了当前图片名称，获取其ID
    if current:
        current_image = db.query(Image).filter(
            Image.file_name == current
        ).first()
        if current_image:
            current_id = current_image.id

    # 从数据库获取随机图片
    db_image = get_random_checked_image(db, current_id)

    # 如果数据库中没有已审核的图片，返回404
    if not db_image:
        # 计算耗时并记录
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"获取随机图片失败 - 执行时间: {execution_time:.3f}秒")
        raise HTTPException(status_code=404, detail="没有可用的图片")

    # 计算耗时并记录
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"成功获取随机图片信息 - 图片ID: {db_image.id}, "
          f"文件名: {db_image.file_name}, 执行时间: {execution_time:.3f}秒")

    # 返回图片信息，优先使用图床URL
    image_url = db_image.image_bed_url
    if not image_url or not image_url.strip():
        image_url = f"/image/checked/{db_image.id}"

    return {
        "id": db_image.id,
        "file_name": db_image.file_name,
        "image_url": image_url,
        "likes": db_image.likes,
        "dislikes": db_image.dislikes,
        "size" : db_image.file_size,
        "width": db_image.width if db_image.width else None,
        "height": db_image.height if db_image.height else None
    }

@app.get("/image/checked/{image_id}")
async def fetch_checked_image(image_id: int, db: Session = Depends(get_db)):
    """从数据库中获取指定ID的已审核图片，通过后端代理获取图片内容"""
    db_image = db.query(Image).filter(Image.id == image_id, Image.is_checked == True).first()

    if not db_image:
        raise HTTPException(status_code=404, detail="未找到该ID的审核图片")

    # 调试信息：打印图片信息
    print(f"获取到图片 - ID: {db_image.id}, 文件名: {db_image.file_name}")
    print(f"图床URL: '{db_image.image_bed_url}'")
    print(f"本地路径: '{db_image.file_path}'")
    
    # 如果有PicGo图床URL，通过后端代理获取图片
    if db_image.image_bed_url and db_image.image_bed_url.strip():
        image_url = db_image.image_bed_url.strip()
        
        if image_url.startswith(('http://', 'https://')):
            try:
                # 通过后端代理获取图片内容
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(image_url)
                    
                    if response.status_code == 200:
                        # 获取图片内容类型
                        content_type = response.headers.get('content-type', 'image/jpeg')
                        # 返回图片内容
                        headers = {
                            "X-Image-Name": db_image.file_name,
                            "X-Image-ID": str(db_image.id),
                            "X-Image-Likes": str(db_image.likes),
                            "X-Image-Dislikes": str(db_image.dislikes),
                            "Cache-Control": "public, max-age=3600"
                        }
                        
                        return Response(
                            content=response.content,
                            media_type=content_type,
                            headers=headers
                        )
                    else:
                        print(f"图床返回错误状态码: {response.status_code}")
                        
            except Exception as e:
                print(f"从图床获取图片失败: {e}")

    # 如果没有图床URL但有本地文件路径，作为后备方案
    if db_image.file_path and os.path.exists(db_image.file_path):
        with open(db_image.file_path, "rb") as image_file:
            content = image_file.read()
        
        media_type = db_image.mime_type
        headers = {
            "X-Image-Name": db_image.file_name,
            "X-Image-ID": str(db_image.id),
            "X-Image-Likes": str(db_image.likes),
            "X-Image-Dislikes": str(db_image.dislikes)
        }
        return Response(content=content, media_type=media_type, headers=headers)
    
    # 如果既没有图床URL也没有本地文件，返回404
    raise HTTPException(status_code=404, detail="图片文件不可用")


@app.get("/image/unchecked/{image_id}")
async def fetch_unchecked_image(image_id: int, db: Session = Depends(get_db)):
    """从数据库中获取指定ID的未审核图片，通过后端代理获取图片内容"""
    db_image = db.query(Image).filter(Image.id == image_id, Image.is_checked == False).first()
    
    if not db_image:
        raise HTTPException(status_code=404, detail="未找到该ID的未审核图片")
    
    # 如果有PicGo图床URL，通过后端代理获取图片
    if db_image.image_bed_url and db_image.image_bed_url.strip():
        image_url = db_image.image_bed_url.strip()
        
        if image_url.startswith(('http://', 'https://')):
            try:
                # 通过后端代理获取图片内容
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(image_url)
                    
                    if response.status_code == 200:
                        # 获取图片内容类型
                        content_type = response.headers.get('content-type', 'image/jpeg')
                        # 返回图片内容
                        headers = {
                            "X-Image-Name": db_image.file_name,
                            "X-Image-ID": str(db_image.id),
                            "Cache-Control": "public, max-age=3600"
                        }
                        
                        return Response(
                            content=response.content,
                            media_type=content_type,
                            headers=headers
                        )
                    else:
                        print(f"图床返回错误状态码: {response.status_code}")
                        
            except Exception as e:
                print(f"从图床获取图片失败: {e}")
    
    # 如果没有图床URL但有本地文件路径，作为后备方案
    if db_image.file_path and os.path.exists(db_image.file_path):
        with open(db_image.file_path, "rb") as image_file:
            content = image_file.read()
        
        media_type = db_image.mime_type
        headers = {
            "X-Image-Name": db_image.file_name,
            "X-Image-ID": str(db_image.id)
        }
        return Response(content=content, media_type=media_type, headers=headers)
    
    # 如果既没有图床URL也没有本地文件，返回404
    raise HTTPException(status_code=404, detail="图片文件不可用")

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """上传图片到PicGo图床并将信息存入数据库"""
    # 检查文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="只允许上传图片文件（JPEG, PNG, GIF, WEBP）"
        )
    
    # 读取文件内容并计算哈希值用于查重
    contents = await file.read()
    file_hash = hashlib.md5(contents).hexdigest()
    await file.seek(0)  # 重置文件指针
    
    # 检查数据库中是否已存在相同哈希值的图片
    existing_image = get_image_by_hash(db, file_hash)
    
    if existing_image:
        return {
            "status": "success", 
            "message": "图片已存在",
            "filename": existing_image.file_name,
            "id": existing_image.id,
            "image_bed_url": existing_image.image_bed_url
        }
    
    # 上传到PicGo图床
    try:
        # 验证 API 密钥
        if not PICGO_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="PicGo API 密钥未设置"
            )

        # 准备请求头
        headers = {
            "X-API-Key": PICGO_API_KEY
        }

        # 准备文件上传数据
        files = {
            "source": (
                file.filename or "image.jpg",
                contents,
                file.content_type
            )
        }        # 准备其他表单数据 - 设置为自动审核通过
        data = {
            "title": f"Meme_{file_hash[:8]}",
            "description": "从Meme系统上传的图片"
        }
        
        # 发送请求到 PicGo API
        print(f"正在发送请求到PicGo API: {PICGO_API_URL}")
        print(f"使用的API密钥: {PICGO_API_KEY[:10]}...{PICGO_API_KEY[-5:]}")
        print(f"数据: {data}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    PICGO_API_URL,
                    headers=headers,
                    files=files,
                    data=data
                )
            print(f"PicGo API响应状态码: {response.status_code}")
            print(f"PicGo API响应内容: {response.text[:200]}")  # 只打印前200个字符避免日志过长
        except Exception as e:
            print(f"PicGo API请求异常: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"请求PicGo API时出错: {str(e)}"
            )

        # 处理响应
        if response.status_code == 200:
            try:
                result = response.json()                # 如果上传成功，保存图片信息到数据库
                if result.get("status_code") == 200:
                    image_info = result["image"]
                    image_bed_url = image_info.get("url", "")
                    
                    if not image_bed_url:
                        raise HTTPException(
                            status_code=500,
                            detail="PicGo返回的图片URL为空"
                        )
                      # 获取图片尺寸信息
                    width = image_info.get("width", 0)
                    height = image_info.get("height", 0)

                    print(width)
                    print(height)
                    # 如果PicGo返回的响应中没有尺寸信息，从本地文件获取
                    if (width == 0 or height == 0) and contents:
                        try:
                            width, height = get_image_dimensions(contents)
                            print(f"从本地文件获取图片尺寸: {width}x{height}")
                        except Exception as e:
                            print(f"获取图片尺寸失败: {e}")
                            width, height = 0, 0
                    
                    # 同时保存图片到本地 unchecked 目录
                    filename = image_info.get("filename", file.filename or f"{file_hash}.jpg")
                    # 确保文件名安全
                    safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
                    if not safe_filename:
                        safe_filename = f"{file_hash}.jpg"
                    
                    local_file_path = os.path.join(UNCHECKED_DIR, safe_filename)
                    
                    # 如果文件已存在，添加数字后缀
                    counter = 1
                    base_path = local_file_path
                    while os.path.exists(local_file_path):
                        name, ext = os.path.splitext(base_path)
                        local_file_path = f"{name}_{counter}{ext}"
                        counter += 1
                    
                    # 保存文件到本地
                    try:
                        with open(local_file_path, "wb") as f:
                            f.write(contents)
                        print(f"图片已保存到本地: {local_file_path}")
                    except Exception as e:
                        print(f"保存本地文件失败: {e}")
                        # 不阻止上传流程，继续执行
                    
                    # 保存图片信息到数据库
                    db_image = add_image(
                        db=db,
                        file_name=filename,
                        file_hash=file_hash,
                        file_path=local_file_path,  # 保存本地路径
                        image_bed_url=image_bed_url,
                        is_checked=False,  # 默认未审核
                        file_size=image_info.get("size", len(contents)),
                        mime_type=image_info.get("mime", file.content_type),
                        width=width,
                        height=height
                    )

                    return {
                        "status": "success", 
                        "message": "图片上传成功", 
                        "filename": db_image.file_name,
                        "id": db_image.id,
                        "image_bed_url": db_image.image_bed_url,
                        "is_checked": db_image.is_checked,
                        "likes": db_image.likes,
                        "dislikes": db_image.dislikes,
                        "file_size": db_image.file_size,
                        "width": db_image.width,
                        "height": db_image.height
                    }
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"PicGo上传失败: {result.get('status_txt', '未知错误')}"
                    )
            except ValueError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"PicGo API 返回的响应格式错误: {str(e)}"
                )
        else:
            # 上传失败
            error_detail = response.text
            try:
                error_json = response.json()
                if "error" in error_json:
                    error_detail = error_json["error"].get("message", error_detail)
                elif "status_txt" in error_json:
                    error_detail = error_json["status_txt"]
            except Exception:
                pass

            raise HTTPException(
                status_code=500,
                detail=f"PicGo上传失败: {error_detail}"
            )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=408,
            detail="上传超时，请重试"
        )
    except HTTPException:
        raise  # 重新抛出已知的HTTP异常
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传失败: {str(e)}"
        )

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
        {
            "id": img.id,
            "file_name": img.file_name,
            "is_checked": img.is_checked,
            "likes": img.likes,
            "dislikes": img.dislikes,
            "image_bed_url": img.image_bed_url or "",
            "file_size": img.file_size
        } for img in images
    ]


@app.post("/image/{image_id}/check")
async def check_image(
    image_id: int,
    is_checked: bool = True,
    db: Session = Depends(get_db)
):
    """更新图片的审核状态"""
    # 先获取图片信息
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if not db_image:
        raise HTTPException(status_code=404, detail="图片未找到")
    
    # 如果是通过审核且有本地文件，移动文件到checked目录
    if is_checked and db_image.file_path and os.path.exists(db_image.file_path):
        try:
            # 从unchecked路径获取文件名
            filename = os.path.basename(db_image.file_path)
            
            # 构建checked目录的新路径
            new_file_path = os.path.join(CHECKED_DIR, filename)
            
            # 如果文件已存在，添加数字后缀
            counter = 1
            base_path = new_file_path
            while os.path.exists(new_file_path):
                name, ext = os.path.splitext(base_path)
                new_file_path = f"{name}_{counter}{ext}"
                counter += 1
            
            # 移动文件
            shutil.move(db_image.file_path, new_file_path)
            print(f"图片文件已移动: {db_image.file_path} -> {new_file_path}")
            
            # 更新数据库中的文件路径
            db_image.file_path = new_file_path
            
        except Exception as e:
            print(f"移动文件失败: {e}")
            # 继续执行，不中断审核流程
    
    # 更新审核状态
    db_image.is_checked = is_checked
    db.commit()
    db.refresh(db_image)
    
    return {
        "id": db_image.id,
        "file_name": db_image.file_name,
        "is_checked": db_image.is_checked,
        "file_path": db_image.file_path,
        "image_bed_url": db_image.image_bed_url or "",
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

# 获取待审核图片列表
@app.get("/admin/pending-images")
async def get_pending_images(
    current_admin: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取待审核的图片列表，返回包含图床URL的图片信息"""
    try:
        print(f"Admin user: {current_admin}")
        images = get_all_unchecked_images(db, skip=0, limit=50)  # 增加限制数量
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
                    "image_url": img.image_bed_url if img.image_bed_url and img.image_bed_url.strip() else f"/image/unchecked/{img.id}",
                    "source": "picgo" if img.image_bed_url and img.image_bed_url.strip() else "local",
                    "width": getattr(img, 'width', 0),
                    "height": getattr(img, 'height', 0),
                    "created_at": img.upload_time.isoformat() if hasattr(img, 'upload_time') and img.upload_time else None
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
    """获取已审核图片列表（分页），返回包含图床URL的图片信息"""
    # 计算跳过的记录数
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
                "image_url": img.image_bed_url if img.image_bed_url and img.image_bed_url.strip() else f"/image/checked/{img.id}",
                "source": "picgo" if img.image_bed_url and img.image_bed_url.strip() else "local",
                "width": getattr(img, 'width', 0),
                "height": getattr(img, 'height', 0),
                "created_at": img.upload_time.isoformat() if hasattr(img, 'upload_time') and img.upload_time else None
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
    
    elif action == "reject":        # 拒绝图片（删除）
        db_image = db.query(Image).filter(Image.id == image_id).first()
        if not db_image:
            raise HTTPException(status_code=404, detail="图片未找到")
        
        # 删除数据库记录（不再删除本地文件，因为使用图床）
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
      # 删除数据库记录（不再删除本地文件，因为使用图床）
    db.delete(db_image)
    db.commit()
    
    return {"message": "图片已删除", "id": image_id}


# PicGo 上传相关模型
class PicGoUploadRequest(BaseModel):
    api_key: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    album_id: Optional[str] = None
    category_id: Optional[str] = None
    width: Optional[int] = None
    expiration: Optional[str] = None
    nsfw: Optional[int] = 0
    format: Optional[str] = "json"
    use_file_date: Optional[int] = 0


class PicGoUploadResponse(BaseModel):
    status_code: int
    success: Optional[dict] = None
    error: Optional[dict] = None
    image: Optional[dict] = None
    status_txt: str


# PicGo 上传 API
@app.post("/upload/picgo", response_model=PicGoUploadResponse)
async def upload_to_picgo(
    file: UploadFile = File(...),
    api_key: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[str] = None,
    album_id: Optional[str] = None,
    category_id: Optional[str] = None,
    width: Optional[int] = None,
    expiration: Optional[str] = None,
    nsfw: Optional[int] = 0,
    format: Optional[str] = "json",
    use_file_date: Optional[int] = 0,
    db: Session = Depends(get_db)
):
    """上传图片到 PicGo 图床，支持指定相册
    
    Args:
        file: 图片文件
        album_id: 相册ID（可选），必须是你的API key用户拥有的相册
        api_key: PicGo API密钥
        title: 图片标题
        description: 图片描述
        tags: 图片标签（逗号分隔）
        category_id: 分类ID
        width: 目标宽度
        expiration: 过期时间（如 PT5M 表示5分钟，P3D 表示3天）
        nsfw: 是否NSFW内容 (0或1)
        format: 返回格式 (json, redirect, txt)
        use_file_date: 使用文件日期而非上传日期 (0或1)
    """

    album_id = "Spkw6"

    # 验证 API 密钥 - 优先使用参数中的api_key，否则使用配置的API密钥
    picgo_key = api_key or PICGO_API_KEY
    if not picgo_key:
        raise HTTPException(
            status_code=400,
            detail="PicGo API 密钥未设置，请在环境变量中设置 PICGO_API_KEY"
        )

    # 检查文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="只允许上传图片文件（JPEG, PNG, GIF, WEBP）"
        )

    try:
        # 读取文件内容
        file_content = await file.read()

        # 准备请求头 - 只包含API密钥，让httpx自动处理multipart/form-data
        headers = {
            "X-API-Key": picgo_key
        }

        # 准备文件上传数据 - 按照curl示例的格式
        files = {
            "source": (
                file.filename or "image.jpg",
                file_content,
                file.content_type
            )
        }

        # 准备其他表单数据
        data = {}
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        if tags:
            data["tags"] = tags
        if album_id:
            data["album_id"] = album_id
        if category_id:
            data["category_id"] = category_id
        if width:
            data["width"] = str(width)
        if expiration:
            data["expiration"] = expiration
        if nsfw is not None:
            data["nsfw"] = str(nsfw)
        if format:
            data["format"] = format
        if use_file_date is not None:
            data["use_file_date"] = str(use_file_date)

        # 发送请求到 PicGo API - 模拟curl命令的行为
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                PICGO_API_URL,
                headers=headers,
                files=files,
                data=data
            )

        # 处理响应
        if response.status_code == 200:
            try:
                result = response.json()

                # 如果上传成功，保存图片信息到数据库
                if result.get("status_code") == 200 and result.get("image"):
                    image_info = result["image"]                    # 计算文件哈希
                    file_hash = hashlib.md5(file_content).hexdigest()
                    
                    # 检查数据库中是否已存在
                    existing_image = get_image_by_hash(db, file_hash)
                    
                    if not existing_image:
                        # 获取图片尺寸信息
                        width = image_info.get("width", 0)
                        height = image_info.get("height", 0)
                        
                        # 如果PicGo返回的响应中没有尺寸信息，从文件内容获取
                        if (width == 0 or height == 0) and file_content:
                            try:
                                width, height = get_image_dimensions(file_content)
                                print(f"从文件内容获取图片尺寸: {width}x{height}")
                            except Exception as e:
                                print(f"获取图片尺寸失败: {e}")
                                width, height = 0, 0
                        
                        # 保存图片信息到数据库
                        db_image = add_image(
                            db=db,
                            file_name=image_info.get("filename", file.filename),
                            file_hash=file_hash,
                            file_path=image_info.get("url", ""),
                            image_bed_url=image_info.get("url", ""),
                            is_checked=True,
                            file_size=image_info.get("size", 0),
                            mime_type=image_info.get(
                                "mime", file.content_type
                            ),
                            width=width,
                            height=height
                        )

                        # 在响应中添加数据库 ID 和相册信息
                        result["database_id"] = db_image.id
                        if album_id:
                            result["uploaded_to_album"] = album_id
                            result["album_upload"] = True
                    else:
                        # 如果图片已存在，仍然记录相册信息
                        if album_id:
                            result["uploaded_to_album"] = album_id
                            result["album_upload"] = True
                            result["note"] = "图片已存在于数据库中"

                return PicGoUploadResponse(**result)
            except ValueError as e:
                # JSON解析失败
                raise HTTPException(
                    status_code=500,
                    detail=f"PicGo API 返回的响应格式错误: {str(e)}"
                )
        else:
            # 上传失败
            error_detail = response.text
            try:
                error_json = response.json()
                if "error" in error_json:
                    error_detail = error_json["error"].get(
                        "message", error_detail
                    )
                elif "status_txt" in error_json:
                    error_detail = error_json["status_txt"]
            except Exception:
                pass

            return PicGoUploadResponse(
                status_code=response.status_code,
                error={
                    "message": error_detail,
                    "code": response.status_code
                },
                status_txt="ERROR"
            )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=408,
            detail="上传超时，请重试"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传失败: {str(e)}"
        )


# 从 URL 上传到 PicGo
@app.post("/upload/picgo-url")
async def upload_url_to_picgo(
    source_url: str,
    api_key: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[str] = None,
    album_id: Optional[str] = None,
    category_id: Optional[str] = None,
    width: Optional[int] = None,
    expiration: Optional[str] = None,
    nsfw: Optional[int] = 0,
    format: Optional[str] = "json",
    use_file_date: Optional[int] = 0
):
    """通过 URL 上传图片到 PicGo 图床"""

    # 验证 API 密钥
    picgo_key = api_key or PICGO_API_KEY
    if not picgo_key:
        raise HTTPException(
            status_code=400,
            detail="PicGo API 密钥未设置"
        )

    try:
        # 准备上传数据
        headers = {
            "X-API-Key": picgo_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "source": source_url
        }

        if title:
            data["title"] = title
        if description:
            data["description"] = description
        if tags:
            data["tags"] = tags
        if album_id:
            data["album_id"] = album_id
        if category_id:
            data["category_id"] = category_id
        if width:
            data["width"] = str(width)
        if expiration:
            data["expiration"] = expiration
        if nsfw is not None:
            data["nsfw"] = str(nsfw)
        if format:
            data["format"] = format
        if use_file_date is not None:
            data["use_file_date"] = str(use_file_date)

        # 发送请求到 PicGo API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                PICGO_API_URL,
                headers=headers,
                data=data
            )

        # 处理响应
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            # 上传失败
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = error_json.get(
                    "error", {}
                ).get("message", error_detail)
            except Exception:
                pass

            raise HTTPException(
                status_code=response.status_code,
                detail=f"PicGo 上传失败: {error_detail}"
            )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=408,
            detail="上传超时，请重试"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传失败: {str(e)}"
        )


# 获取 PicGo 配置状态
@app.get("/picgo/status")
async def get_picgo_status():
    """获取 PicGo 配置状态"""
    return {
        "api_configured": bool(PICGO_API_KEY),
        "api_url": PICGO_API_URL,
        "has_api_key": bool(PICGO_API_KEY)
    }


# 专门上传到指定相册的端点
@app.post("/upload/picgo/album/{album_id}")
async def upload_to_picgo_album(
    album_id: str,
    file: UploadFile = File(...),
    api_key: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """直接上传图片到指定相册
    
    Args:
        album_id: 相册ID（路径参数）
        file: 图片文件
        api_key: PicGo API密钥
        title: 图片标题
        description: 图片描述
        tags: 图片标签（逗号分隔）
    """
    
    # 调用主上传函数，指定相册ID
    return await upload_to_picgo(
        file=file,
        api_key=api_key,
        title=title,
        description=description,
        tags=tags,
        album_id=album_id,  # 使用路径中的相册ID
        db=db
    )


# 批量上传到相册的端点
@app.post("/upload/picgo/album/{album_id}/batch")
async def batch_upload_to_album(
    album_id: str,
    files: List[UploadFile] = File(...),
    api_key: Optional[str] = None,
    titles: Optional[str] = None,  # 逗号分隔的标题列表
    description: Optional[str] = None,
    tags: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """批量上传图片到指定相册
    
    Args:
        album_id: 相册ID
        files: 图片文件列表
        api_key: PicGo API密钥
        titles: 图片标题列表（逗号分隔，对应文件顺序）
        description: 通用描述
        tags: 通用标签
    """
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="一次最多上传10张图片")
    
    # 解析标题列表
    title_list = []
    if titles:
        title_list = [title.strip() for title in titles.split(',')]
    
    results = []
    success_count = 0
    
    for i, file in enumerate(files):
        try:
            # 为每个文件分配标题
            file_title = title_list[i] if i < len(title_list) else None
            
            result = await upload_to_picgo(
                file=file,
                api_key=api_key,
                title=file_title,
                description=description,
                tags=tags,
                album_id=album_id,
                db=db
            )
            
            results.append({
                "filename": file.filename,
                "success": True,
                "result": result.dict() if hasattr(result, 'dict') else result
            })
            success_count += 1
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    return {
        "album_id": album_id,
        "total_files": len(files),
        "results": results,
        "success_count": success_count,
        "error_count": len(files) - success_count
    }


# 相册信息模型
class AlbumUploadSummary(BaseModel):
    """相册上传摘要"""
    album_id: str
    total_uploaded: int
    success_count: int
    error_count: int
    uploaded_files: List[str]


# 获取相册上传统计
@app.get("/picgo/album/{album_id}/stats")
async def get_album_upload_stats(
    album_id: str,
    api_key: Optional[str] = None
):
    """获取指定相册的上传统计信息
    
    Args:
        album_id: 相册ID
        api_key: PicGo API密钥
    """
    
    picgo_key = api_key or PICGO_API_KEY
    if not picgo_key:
        raise HTTPException(
            status_code=400,
            detail="PicGo API 密钥未设置"
        )
    
    # 这里可以根据需要实现获取相册统计的逻辑
    # 目前返回基本信息
    return {
        "album_id": album_id,
        "message": f"相册 {album_id} 统计信息",
        "note": "此功能需要根据PicGo API具体实现"
    }


# 添加获取图片尺寸的辅助函数
def get_image_dimensions(image_content: bytes) -> tuple[int, int]:
    """从图片二进制数据获取宽度和高度"""
    try:
        with PILImage.open(BytesIO(image_content)) as img:
            return img.size  # 返回 (width, height)
    except Exception as e:
        print(f"获取图片尺寸失败: {e}")
        return (0, 0)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

