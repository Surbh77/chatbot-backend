from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from retriver_module import generate
from fastapi.middleware.cors import CORSMiddleware

import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ask_questionrequest(BaseModel):
    question: str
    
class read_document_request(BaseModel):
    document_id: str 

@app.get("/")
def read_root():
    return {"message": "Welcome to the PDF Upload API. Use the /upload-pdf/ endpoint to upload and read a PDF file."}


@app.post("/ask_question/")
async def ask_question(payload:ask_questionrequest):
    # Ensure the uploaded file is a PDF


    try:
        response = generate(payload.question)
        

        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the PDF: {str(e)}")