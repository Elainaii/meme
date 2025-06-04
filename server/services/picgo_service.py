# PicGo 服务逻辑
import httpx
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, Tuple

# 导入日志
from logger_config import get_logger

from config import PICGO_API_URL, PICGO_API_KEY
from database import add_image, get_image_by_hash
from utils.image_utils import calculate_file_hash, get_image_dimensions
from models import PicGoUploadResponse

logger = get_logger(__name__)


class PicGoService:
    """PicGo 图床服务"""
    
    def __init__(self):
        self.api_url = PICGO_API_URL
        self.api_key = PICGO_API_KEY
    
    async def upload_file(
        self,
        file: UploadFile,
        db: Session,
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
        auto_check: bool = False
    ) -> Dict[str, Any]:
        """上传文件到PicGo图床"""
        
        # 验证API密钥
        picgo_key = api_key or self.api_key
        if not picgo_key:
            raise HTTPException(
                status_code=500,
                detail="PicGo API 密钥未设置"
            )
        
        # 读取文件内容
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
        
        # 上传到PicGo
        try:
            result = await self._upload_to_picgo(
                file_content=contents,
                filename=file.filename,
                content_type=file.content_type,
                picgo_key=picgo_key,
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
            
            # 保存到数据库
            if result.get("status_code") == 200 and result.get("image"):
                db_image = await self._save_to_database(
                    db=db,
                    image_info=result["image"],
                    file_content=contents,
                    file_hash=file_hash,
                    original_filename=file.filename,
                    content_type=file.content_type,
                    is_checked=auto_check
                )
                
                result["database_id"] = db_image.id
                if album_id:
                    result["uploaded_to_album"] = album_id
                    result["album_upload"] = True
            
            return result
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"上传失败: {str(e)}"
            )
    
    async def upload_from_url(
        self,
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
    ) -> Dict[str, Any]:
        """通过URL上传图片到PicGo"""
        
        picgo_key = api_key or self.api_key
        if not picgo_key:
            raise HTTPException(
                status_code=400,
                detail="PicGo API 密钥未设置"
            )
        
        try:
            headers = {
                "X-API-Key": picgo_key,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {"source": source_url}
            
            # 添加可选参数
            optional_params = {
                "title": title,
                "description": description,
                "tags": tags,
                "album_id": album_id,
                "category_id": category_id,
                "width": width,
                "expiration": expiration,
                "nsfw": nsfw,
                "format": format,
                "use_file_date": use_file_date
            }
            
            for key, value in optional_params.items():
                if value is not None:
                    data[key] = str(value)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    data=data
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("error", {}).get("message", error_detail)
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
    
    async def _upload_to_picgo(
        self,
        file_content: bytes,
        filename: Optional[str],
        content_type: str,
        picgo_key: str,
        **kwargs
    ) -> Dict[str, Any]:
        """实际上传到PicGo的内部方法"""
        
        headers = {"X-API-Key": picgo_key}
        
        files = {
            "source": (
                filename or "image.jpg",
                file_content,
                content_type
            )
        }
          # 准备表单数据
        data = {}
        for key, value in kwargs.items():
            if value is not None:
                data[key] = str(value)
        
        logger.debug(f"正在发送请求到PicGo API: {self.api_url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                files=files,
                data=data
            )
        
        logger.debug(f"PicGo API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status_code") == 200:
                return result
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"PicGo上传失败: {result.get('status_txt', '未知错误')}"
                )
        else:
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
    
    async def _save_to_database(
        self,
        db: Session,
        image_info: Dict[str, Any],
        file_content: bytes,
        file_hash: str,
        original_filename: Optional[str],
        content_type: str,
        is_checked: bool = False
    ):
        """保存图片信息到数据库"""
        
        image_bed_url = image_info.get("url", "")
        if not image_bed_url:
            raise HTTPException(
                status_code=500,
                detail="PicGo返回的图片URL为空"
            )
        
        # 获取图片尺寸
        width = image_info.get("width", 0)
        height = image_info.get("height", 0)
        if (width == 0 or height == 0) and file_content:
            try:
                width, height = get_image_dimensions(file_content)
                logger.debug(f"从本地文件获取图片尺寸: {width}x{height}")
            except Exception as e:
                logger.error(f"获取图片尺寸失败: {e}")
                width, height = 0, 0
        
        # 保存到数据库
        filename = image_info.get("filename", original_filename or f"{file_hash}.jpg")
        
        db_image = add_image(
            db=db,
            file_name=filename,
            file_hash=file_hash,
            file_path="",  # PicGo上传不保存本地路径
            image_bed_url=image_bed_url,
            is_checked=is_checked,
            file_size=image_info.get("size", len(file_content)),
            mime_type=image_info.get("mime", content_type),
            width=width,
            height=height
        )
        
        return db_image
    
    def get_status(self) -> Dict[str, Any]:
        """获取PicGo配置状态"""
        return {
            "api_configured": bool(self.api_key),
            "api_url": self.api_url,
            "has_api_key": bool(self.api_key)
        }


# 创建全局服务实例
picgo_service = PicGoService()
