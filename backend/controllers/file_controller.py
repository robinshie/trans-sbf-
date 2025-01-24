from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from backend.services.file_service import FileService
from backend.schemas.chat import FileResponse as FileResponseSchema
import os
import json
from datetime import datetime

router = APIRouter()

# 存储PDF内容的字典
pdf_contents = {}

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    file_service: FileService = Depends(lambda: FileService())
):
    """文件上传接口"""
    try:
        # 验证文件类型
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # 提取文本
        text = await file_service.extract_pdf_text(file)
        if not text:
            raise HTTPException(status_code=400, detail="Failed to extract text from PDF")
        
        # 保存文件
        file_path = await file_service.save_upload_file(file)
        
        # 存储PDF内容用于后续对话
        pdf_contents[file.filename] = {
            'text': text,
            'file_path': file_path,
            'timestamp': str(datetime.now())
        }
        
        return FileResponseSchema(
            text=text,
            filename=file.filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pdf/{filename}")
async def get_pdf(
    filename: str,
    file_service: FileService = Depends(lambda: FileService())
):
    """获取PDF文件接口"""
    try:
        file_path = os.path.join(file_service.settings.UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PDF file not found")
            
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pdf/content/{filename}")
async def get_pdf_content(filename: str):
    """获取PDF内容接口"""
    if filename not in pdf_contents:
        raise HTTPException(status_code=404, detail="PDF content not found")
    return pdf_contents[filename]
