import os
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from kreuzberg import extract_file, extract_bytes
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document Text Extraction API",
    description="API for extracting text from various document formats using kreuzberg",
    version="1.0.0"
)

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_mime_type(file_path: str) -> str:
    mime_type = ""
    if file_path.endswith('.pdf'):
        mime_type = 'application/pdf'
    elif file_path.endswith(('.png', '.jpg', '.jpeg')):
        mime_type = 'image/jpeg'
    elif file_path.endswith('.docx'):
        mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif file_path.endswith('.doc'):
        mime_type = 'application/msword'
    elif file_path.endswith('.txt'):
        mime_type = 'text/plain'
    elif file_path.endswith('.pptx'):
        mime_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    elif file_path.endswith('.ppt'):
        mime_type = 'application/vnd.ms-powerpoint'
    elif file_path.endswith('.xlsx'):
        mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif file_path.endswith('.xls'):
        mime_type = 'application/vnd.ms-excel'
    elif file_path.endswith('.csv'):
        mime_type = 'text/csv'
    elif file_path.endswith('.html'):
        mime_type = 'text/html'
    elif file_path.endswith('.xml'):
        mime_type = 'application/xml'
    return mime_type

@app.post("/extract")
async def extract_text_from_file(file: UploadFile = File(...)):
    """
    Extract text from an uploaded file.
    Supports PDF, images (png, jpg, etc.), and Word documents.
    """
    try:
        logger.info(f"Processing file: {file.filename}")
        file_bytes = await file.read()
        
        mime_type = get_mime_type(file.filename)
        if not mime_type:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type"
            )
        
        # Process the file using the raw bytes
        result = await extract_bytes(file_bytes, mime_type=mime_type)
        
        logger.info(f"Successfully processed file: {file.filename}")
        return {
            "filename": file.filename,
            "content": result.content
        }
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        workers=int(os.getenv("WORKERS", "4")),
        loop="uvloop",
        http="httptools",
        log_config=None,  # Disable uvicorn default logging in favor of JSON logging
    )