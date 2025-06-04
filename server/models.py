# 数据模型和响应模型
from pydantic import BaseModel
from typing import List, Optional


class ImageInfo(BaseModel):
    id: int
    file_name: str
    is_checked: bool
    likes: int
    dislikes: int
    
    class Config:
        from_attributes = True


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


class AlbumUploadSummary(BaseModel):
    """相册上传摘要"""
    album_id: str
    total_uploaded: int
    success_count: int
    error_count: int
    uploaded_files: List[str]
