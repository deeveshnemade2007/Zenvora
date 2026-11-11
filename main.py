"""Zenvora backend (Render Python runtime, no Docker): pure-Python PDF tools + serves ./static."""
import os, re, shutil, tempfile, zipfile, pathlib

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

MAX_MB = int(os.getenv("MAX_UPLOAD_MB", "20"))
PDF = {".pdf"}

app = FastAPI(title="Zenvora API")


def workdir(bg: BackgroundTasks) -> pathlib.Path:
    d = tempfile.mkdtemp(prefix="zv_")
    bg.add_task(shutil.rmtree, d, True)  # removed after the response is sent
    return pathlib.Path(d)


def store(up: UploadFile, d: pathlib.Path, allowed: set) -> pathlib.Path:
    name = re.sub(r"[^A-Za-z0-9._-]", "_", pathlib.Path(up.filename or "file").name)
    ext = pathlib.Path(name).suffix.lower()
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(allowed))}")
    p, size = d / name, 0
    with p.open("wb") as f:
        while chunk := up.file.read(1 << 20):
            size += len(chunk)
            if size > MAX_MB * 1048576:
                raise HTTPException(413, f"File too large (max {MAX_MB} MB)")
            f.write(chunk)
    return p


def not_here(name: str):
    raise HTTPException(501, f"{name} isn't available on this deployment (it needs the Docker version of Zenvora).")


# ---------- tools that work without Docker ----------
@app.post("/api/compress")
def compress(bg: BackgroundTasks, file: UploadFile = File(...)):
    import pymupdf
    d = workdir(bg)
    src = store(file, d, PDF)
    out = d / "out.pdf"
    try:
        doc = pymupdf.open(src)
        try:  # shrink large images (PyMuPDF 1.24.2+)
            doc.rewrite_images(dpi_threshold=150, dpi_target=110, quality=60)
        except Exception:
            pass
        doc.save(out, garbage=4, deflate=True, clean=True)
        doc.close()
    except Exception as e:
        raise HTTPException(422, f"Couldn't compress this PDF: {e}")
    if out.stat().st_size >= src.stat().st_size:
        out = src  # already as small as it gets
    return FileResponse(out, filename=f"{src.stem}-compressed.pdf", media_type="application/pdf")


@app.post("/api/repair")
def repair(bg: BackgroundTasks, file: UploadFile = File(...)):
    import pymupdf
    d = workdir(bg)
    src = store(file, d, PDF)
    out = d / "out.pdf"
    try:
        doc = pymupdf.open(src)  # PyMuPDF rebuilds broken xref tables on open
        doc.save(out, garbage=4, deflate=True)
        doc.close()
    except Exception as e:
        raise HTTPException(422, f"This PDF is too damaged to recover: {e}")
    return FileResponse(out, filename=f"{src.stem}-repaired.pdf", media_type="application/pdf")


@app.post("/api/pdf-to-images")
def pdf_to_images(bg: BackgroundTasks, file: UploadFile = File(...),
                  fmt: str = Query("png"), dpi: int = Query(150)):
    import pymupdf
    ext = "jpg" if fmt in {"jpg", "jpeg"} else "png"
    dpi = min(max(dpi, 72), 200)
    d = workdir(bg)
    src = store(file, d, PDF)
    z = d / "pages.zip"
    try:
        with pymupdf.open(src) as doc, zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, page in enumerate(doc, 1):
                img = d / f"page-{i}.{ext}"
                page.get_pixmap(dpi=dpi).save(img)
                zf.write(img, img.name)
                img.unlink()
    except Exception as e:
        raise HTTPException(422, f"Couldn't render this PDF: {e}")
    return FileResponse(z, filename=f"{src.stem}-pages.zip", media_type="application/zip")


@app.post("/api/pdf-to-word")
def pdf_to_word(bg: BackgroundTasks, file: UploadFile = File(...)):
    from pdf2docx import Converter
    d = workdir(bg)
    src = store(file, d, PDF)
    out = d / "out.docx"
    try:
        cv = Converter(str(src))
        cv.convert(str(out))
        cv.close()
    except Exception as e:
        raise HTTPException(422, f"Couldn't convert this PDF: {e}")
    if not out.exists():
        raise HTTPException(422, "Nothing could be extracted (scanned PDF?)")
    return FileResponse(out, filename=f"{src.stem}.docx",
                        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@app.post("/api/pdf-to-excel")
def pdf_to_excel(bg: BackgroundTasks, file: UploadFile = File(...)):
    import openpyxl, pdfplumber
    d = workdir(bg)
    src = store(file, d, PDF)
    wb, n = openpyxl.Workbook(), 0
    wb.remove(wb.active)
    try:
        with pdfplumber.open(src) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                for j, table in enumerate(page.extract_tables(), 1):
                    ws = wb.create_sheet(f"p{i}-t{j}"[:31])
                    n += 1
                    for row in table:
                        ws.append([("" if c is None else str(c)) for c in row])
    except Exception as e:
        raise HTTPException(422, f"Couldn't read this PDF: {e}")
    if n == 0:
        raise HTTPException(422, "No tables found in this PDF.")
    out = d / "out.xlsx"
    wb.save(out)
    return FileResponse(out, filename=f"{src.stem}.xlsx",
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ---------- tools that need the Docker version ----------
@app.post("/api/ocr")
def ocr(): not_here("OCR PDF")

@app.post("/api/pdf-to-ppt")
def pdf_to_ppt(): not_here("PDF to PPT")

@app.post("/api/office-to-pdf")
def office_to_pdf(): not_here("Word/PPT/Excel to PDF")

@app.post("/api/html-to-pdf")
def html_to_pdf(): not_here("HTML to PDF")


@app.get("/api/health")
def health():
    return {"ok": True}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
