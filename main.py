from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from utils.generator import generate_excel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
async def generate(request: Request, year: int = Form(...)):
    output_path = generate_excel(year)
    return FileResponse(path=output_path, filename=Path(output_path).name, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
