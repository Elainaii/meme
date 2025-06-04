# 管理员相关路由
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# 导入日志
from logger_config import get_logger

from database import (
    get_db, Image, get_all_unchecked_images, get_all_checked_images,
    update_image_checked_status
)
from config import verify_admin_password, ACCESS_TOKEN_EXPIRE_MINUTES
from auth import create_access_token, get_current_admin_user
from models import AdminLoginRequest, AdminLoginResponse

router = APIRouter()
logger = get_logger(__name__)


@router.post("/admin/verify", response_model=AdminLoginResponse)
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


@router.get("/admin/pending-images")
async def get_pending_images(
    current_admin: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取待审核的图片列表，返回包含图床URL的图片信息"""
    try:
        logger.debug(f"Admin user: {current_admin}")
        images = get_all_unchecked_images(db, skip=0, limit=50)  # 增加限制数量
        logger.debug(f"Found {len(images)} unchecked images")
        
        # 获取总数
        total = db.query(Image).filter(Image.is_checked == False).count()
        logger.debug(f"Total unchecked images: {total}")
        
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
        logger.debug(f"Returning {len(result['images'])} pending images")
        return result
    except Exception as e:
        logger.error(f"Error in get_pending_images: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/admin/checked-images")
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


@router.post("/admin/review-image/{image_id}")
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
        
        # 删除数据库记录（不再删除本地文件，因为使用图床）
        db.delete(db_image)
        db.commit()
        
        return {"message": "图片已拒绝并删除", "action": "rejected"}


@router.delete("/admin/image/{image_id}")
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
