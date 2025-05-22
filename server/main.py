from fastapi import FastAPI,File,Response
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
#upload,login(key),etc
@app.get("/image")
async def fetch_image():#之后改为从数据库中获取文件名
    with open("images/example.jpg", "rb") as image_file:
        content = image_file.read()
    return Response(content=content, media_type="image/jpeg")
'''
@app.get("/image/checked/{image_id}")
@app.get("/image/unchecked/{image_id}")


@app.post("/upload/")#上传图片,获取时间，计算哈希查重
async def upload_image():
    pass
'''