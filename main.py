from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pymupdf  
import base64

app = FastAPI(title="PDF to Images API")


@app.post("/pdf-to-images")
async def convert_pdf_to_images(
    file: UploadFile = File(...),
    dpi: int = 300
):
    # Validate file
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    try:
        pdf_bytes = await file.read()

        
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

        images = []

        zoom = dpi / 72
        matrix = pymupdf.Matrix(zoom, zoom)

        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=matrix)

            img_bytes = pix.tobytes("png")

            images.append({
                "page": i + 1,
                "width": pix.width,
                "height": pix.height,
                "image": base64.b64encode(img_bytes).decode()
            })

        return JSONResponse(content={
            "total_pages": len(images),
            "images": images
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))