import fitz  # PyMuPDF
import io
import re
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Izinkan CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PDF_PATH = "dokumen.pdf"

@app.get("/")
def get_index():
    return FileResponse("index.html")

@app.get("/data.json")
def get_data():
    return FileResponse("data.json")

@app.get("/dokumen.pdf")
def get_pdf():
    return FileResponse(PDF_PATH)

# Endpoint pemotong PDF instan & hemat memori
@app.get("/api/split")
def split_pdf(
    start: int = Query(..., description="Halaman awal"),
    end: int = Query(..., description="Halaman akhir"),
    name: str = Query("dokumen", description="Nama file")
):
    try:
        doc = fitz.open(PDF_PATH)
        total_pages = len(doc)

        if start < 1 or end > total_pages or start > end:
            raise HTTPException(status_code=400, detail="Rentang halaman tidak valid.")

        # Buat dokumen PDF baru hanya untuk rentang halaman tersebut
        new_doc = fitz.open()
        # insert_pdf menggunakan indeks berbasis 0: from_page s/d to_page
        new_doc.insert_pdf(doc, from_page=start - 1, to_page=end - 1)

        # Simpan hasil potongan ke memori stream (RAM ringan)
        pdf_bytes = new_doc.tobytes(garbage=3, deflate=True)
        new_doc.close()
        doc.close()

        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        filename = f"{safe_name}_Hal_{start}-{end}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Server aktif! Buka browser di http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)