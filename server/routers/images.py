# 图片相关路由
import os
import time
import httpx
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Optional

# 导入日志
from logger_config import get_logger

from database import (
    get_db, Image, get_random_checked_image, get_all_checked_images, 
    get_all_unchecked_images, update_image_likes, update_image_dislikes,
    update_image_checked_status
)
from models import ImageInfo
from config import CHECKED_DIR, UNCHECKED_DIR
import shutil

router = APIRouter()
logger = get_logger(__name__)


@router.get("/image-info")
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


@router.get("/image")
async def fetch_random_image(current: str = "", db: Session = Depends(get_db)):
    """从数据库随机获取一张已审核的图片，返回图片信息和图床URL"""
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
    db_image = get_random_checked_image(db, current_id)    # 如果数据库中没有已审核的图片，返回404
    if not db_image:
        # 计算耗时并记录
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"获取随机图片失败 - 执行时间: {execution_time:.3f}秒")
        raise HTTPException(status_code=404, detail="没有可用的图片")

    # 计算耗时并记录
    end_time = time.time()
    execution_time = end_time - start_time
    logger.debug(f"成功获取随机图片信息 - 图片ID: {db_image.id}, "
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
        "size": db_image.file_size,
        "width": db_image.width if db_image.width else None,
        "height": db_image.height if db_image.height else None
    }


@router.get("/image/checked/{image_id}")
async def fetch_checked_image(image_id: int, db: Session = Depends(get_db)):
    """从数据库中获取指定ID的已审核图片，通过后端代理获取图片内容"""
    db_image = db.query(Image).filter(Image.id == image_id, Image.is_checked == True).first()

    if not db_image:
        raise HTTPException(status_code=404, detail="未找到该ID的审核图片")

    # 调试信息：记录图片信息
    logger.debug(f"获取到图片 - ID: {db_image.id}, 文件名: {db_image.file_name}")
    logger.debug(f"图床URL: '{db_image.image_bed_url}'")
    logger.debug(f"本地路径: '{db_image.file_path}'")
    
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
                        logger.warning(f"图床返回错误状态码: {response.status_code}")
                        
            except Exception as e:
                logger.error(f"从图床获取图片失败: {e}")

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


@router.get("/image/unchecked/{image_id}")
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
                        logger.warning(f"图床返回错误状态码: {response.status_code}")
                        
            except Exception as e:
                logger.error(f"从图床获取图片失败: {e}")
    
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


@router.post("/image/{image_id}/like")
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


@router.post("/image/{image_id}/dislike")
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


@router.get("/images/list")
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


@router.post("/image/{image_id}/check")
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
