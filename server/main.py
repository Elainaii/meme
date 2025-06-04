# 主应用文件
import time
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# 导入日志配置
from logger_config import get_logger

# 导入数据库相关模块
from database import get_db, create_tables

# 导入路由
from routers import images, upload, admin

# 导入配置和工具
from config import (
    CORS_ORIGINS, API_TITLE, API_DESCRIPTION, API_VERSION,
    DEBUG, SERVER_HOST, SERVER_PORT
)
from utils.image_utils import ensure_directories, setup_example_image

app = FastAPI(title=API_TITLE, description=API_DESCRIPTION, version=API_VERSION)

# 初始化日志
logger = get_logger(__name__)


# 在应用启动时创建数据库表并执行迁移
@app.on_event("startup")
async def startup_db_client():
    logger.info("正在启动应用...")
    logger.info("创建数据库表...")
    create_tables()
    logger.info("确保目录结构存在...")
    ensure_directories()
    logger.info("设置示例图片...")
    setup_example_image()
    logger.info("应用启动完成")


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点，用于监控服务状态"""
    try:
        # 检查数据库连接
        db = next(get_db())
        # 简单地尝试获取数据库会话
        db.close()
        
        logger.debug("健康检查通过")
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "database": "connected",
            "service": "running"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        raise HTTPException(status_code=503, detail={
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e)
        })


@app.get("/test-cors")
async def test_cors():
    """测试CORS端点"""
    logger.debug("CORS测试端点被调用")
    return {"message": "CORS正常工作", "status": "success"}


# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，这样可以确保CORS不会阻止请求
    allow_credentials=False,  # 当使用通配符时必须设置为False
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
logger.info("注册路由...")
app.include_router(images.router, tags=["images"])
app.include_router(upload.router, tags=["upload"])
app.include_router(admin.router, tags=["admin"])
logger.info("路由注册完成")


if __name__ == "__main__":
    import uvicorn
    from config import SERVER_HOST, SERVER_PORT, DEBUG
    
    logger.info(f"启动Uvicorn服务器，监听 {SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"调试模式: {DEBUG}")
    
    uvicorn.run(
        app, 
        host=SERVER_HOST, 
        port=SERVER_PORT,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info"
    )
