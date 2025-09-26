from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
import io
from typing import List, Dict
import zipfile
from PIL import Image
import base64
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Export Service")

class ExportService:
    def export_to_xlsx(self, data: List[Dict]) -> bytes:
        """Экспорт данных в XLSX формат"""
        try:
            df = pd.DataFrame(data)
            
            # Создание Excel файла в памяти
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Coordinates', index=False)
            
            output.seek(0)
            logger.info(f"Exported {len(data)} records to XLSX")
            return output.getvalue()
        except Exception as e:
            logger.error(f"Error exporting to XLSX: {e}")
            raise HTTPException(status_code=500, detail="Failed to export to XLSX")
    
    def export_images_zip(self, images_data: List[Dict]) -> bytes:
        """Экспорт изображений в ZIP архив"""
        try:
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for i, image_data in enumerate(images_data):
                    # Декодирование base64 изображения
                    image_bytes = base64.b64decode(image_data['image'])
                    
                    # Добавление в ZIP
                    filename = f"building_{i+1}_{image_data.get('coordinates', 'unknown')}.jpg"
                    zip_file.writestr(filename, image_bytes)
            
            zip_buffer.seek(0)
            logger.info(f"Exported {len(images_data)} images to ZIP")
            return zip_buffer.getvalue()
        except Exception as e:
            logger.error(f"Error exporting images to ZIP: {e}")
            raise HTTPException(status_code=500, detail="Failed to export images")

export_service = ExportService()

@app.post("/export/xlsx")
async def export_xlsx(data: List[Dict]):
    """Экспорт данных в XLSX"""
    try:
        xlsx_data = export_service.export_to_xlsx(data)
        
        return StreamingResponse(
            io.BytesIO(xlsx_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=coordinates.xlsx"}
        )
    except Exception as e:
        logger.error(f"Error in XLSX export endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export/images")
async def export_images(images_data: List[Dict]):
    """Экспорт изображений в ZIP"""
    try:
        zip_data = export_service.export_images_zip(images_data)
        
        return StreamingResponse(
            io.BytesIO(zip_data),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=buildings_images.zip"}
        )
    except Exception as e:
        logger.error(f"Error in images export endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {
        "status": "healthy",
        "service": "export-service"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
