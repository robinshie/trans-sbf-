import os
from typing import Optional
import PyPDF2
from fastapi import UploadFile
from backend.config.settings import get_settings

settings = get_settings()

class FileService:
    """文件服务"""
    
    @staticmethod
    async def save_upload_file(file: UploadFile) -> str:
        """保存上传的文件"""
        # 确保上传目录存在
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # 生成文件路径
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        
        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
            
        return file_path
    
    @staticmethod
    async def extract_pdf_text(file: UploadFile) -> Optional[str]:
        """从PDF文件中提取文本"""
        try:
            content = await file.read()
            
            # 创建临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # 从临时文件读取PDF
            pdf_reader = PyPDF2.PdfReader(temp_file_path)
            
            # 提取所有页面的文本
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
                
            # 删除临时文件
            os.unlink(temp_file_path)
                
            return text.strip()
        except Exception as e:
            print(f"Error extracting PDF text: {str(e)}")
            return None
        finally:
            await file.seek(0)  # 重置文件指针
