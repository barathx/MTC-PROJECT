import asyncio
from winsdk.windows.graphics.imaging import BitmapDecoder
from winsdk.windows.media.ocr import OcrEngine
from winsdk.windows.storage.streams import RandomAccessStreamReference
from winsdk.windows.storage import StorageFile
import os
import sys

async def run_ocr(image_path):
    try:
        abs_path = os.path.abspath(image_path)
        file = await StorageFile.get_file_from_path_async(abs_path)
        stream = await file.open_async(0) # 0 = Read
        
        decoder = await BitmapDecoder.create_async(stream)
        bitmap = await decoder.get_software_bitmap_async()
        
        engine = OcrEngine.try_create_from_user_profile_languages()
        if not engine:
            return "OCR_ERROR: No engine"
            
        result = await engine.recognize_async(bitmap)
        return result.text
    except Exception as e:
        return f"OCR_ERROR: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = asyncio.run(run_ocr(sys.argv[1]))
        print(text)
