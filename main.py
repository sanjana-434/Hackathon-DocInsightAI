from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import os
from services import process_pdf, get_response
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

class Query(BaseModel):
    question: str

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    try:
        vector_store = await process_pdf(files)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(query: Query):
    try:
        response = await get_response(query.question)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    