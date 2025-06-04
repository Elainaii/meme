# 上传相关路由
import os
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

# 导入日志
from logger_config import get_logger

from database import get_db, add_image, get_image_by_hash
from services.picgo_service import picgo_service
from utils.image_utils import (
    validate_image_type, calculate_file_hash, create_safe_filename, 
    get_unique_filepath, get_image_dimensions
)
from config import UNCHECKED_DIR
from models import PicGoUploadResponse

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload/")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """上传图片到PicGo图床并将信息存入数据库"""
    # 检查文件类型
    if not validate_image_type(file.content_type):
        raise HTTPException(
            status_code=400, 
            detail="只允许上传图片文件（JPEG, PNG, GIF, WEBP）"
        )
    
    # 读取文件内容并计算哈希值用于查重
    contents = await file.read()
    file_hash = calculate_file_hash(contents)
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
    
    # 使用PicGo服务上传
    try:
        result = await picgo_service.upload_file(
            file=file,
            db=db,
            title=f"Meme_{file_hash[:8]}",
            description="从Meme系统上传的图片",
            auto_check=False  # 默认未审核
        )
        
        return {
            "status": "success", 
            "message": "图片上传成功", 
            "filename": result.get("filename"),
            "id": result.get("database_id"),
            "image_bed_url": result.get("image", {}).get("url", ""),
            "is_checked": False,
            "likes": 0,
            "dislikes": 0,
            "file_size": result.get("image", {}).get("size", 0),
            "width": result.get("image", {}).get("width", 0),
            "height": result.get("image", {}).get("height", 0)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传失败: {str(e)}"
        )


@router.post("/upload/picgo", response_model=PicGoUploadResponse)
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
    """上传图片到 PicGo 图床，支持指定相册"""
    
    # 检查文件类型
    if not validate_image_type(file.content_type):
        raise HTTPException(
            status_code=400,
            detail="只允许上传图片文件（JPEG, PNG, GIF, WEBP）"
        )
    
    # 设置默认相册
    if not album_id:
        album_id = "Spkw6"
    
    try:
        result = await picgo_service.upload_file(
            file=file,
            db=db,
            api_key=api_key,
            title=title,
            description=description,
            tags=tags,
            album_id=album_id,
            category_id=category_id,
            width=width,
            expiration=expiration,
            nsfw=nsfw,
            format=format,
            use_file_date=use_file_date,
            auto_check=True  # PicGo直接上传默认自动审核通过
        )
        
        return PicGoUploadResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传失败: {str(e)}"
        )


@router.post("/upload/picgo-url")
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
    
    try:
        result = await picgo_service.upload_from_url(
            source_url=source_url,
            api_key=api_key,
            title=title,
            description=description,
            tags=tags,
            album_id=album_id,
            category_id=category_id,
            width=width,
            expiration=expiration,
            nsfw=nsfw,
            format=format,
            use_file_date=use_file_date
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传失败: {str(e)}"
        )


@router.post("/upload/picgo/album/{album_id}")
async def upload_to_picgo_album(
    album_id: str,
    file: UploadFile = File(...),
    api_key: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """直接上传图片到指定相册"""
    
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


@router.post("/upload/picgo/album/{album_id}/batch")
async def batch_upload_to_album(
    album_id: str,
    files: List[UploadFile] = File(...),
    api_key: Optional[str] = None,
    titles: Optional[str] = None,  # 逗号分隔的标题列表
    description: Optional[str] = None,
    tags: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """批量上传图片到指定相册"""
    
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


@router.get("/picgo/status")
async def get_picgo_status():
    """获取 PicGo 配置状态"""
    return picgo_service.get_status()


@router.get("/picgo/album/{album_id}/stats")
async def get_album_upload_stats(
    album_id: str,
    api_key: Optional[str] = None
):
    """获取指定相册的上传统计信息"""
    
    # 这里可以根据需要实现获取相册统计的逻辑
    # 目前返回基本信息
    return {
        "album_id": album_id,
        "message": f"相册 {album_id} 统计信息",
        "note": "此功能需要根据PicGo API具体实现"
    }
