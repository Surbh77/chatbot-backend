from fastapi import FastAPI, File, UploadFile, HTTPException,Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ingester_modules import document_ingest, delete_doc, read_doc ,get_all_doc
from retriver_module import generate

import os
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class upload_document_Request(BaseModel):
    uploader_name: str
class delete_document_request(BaseModel):
    document_id: str
    
class read_document_request(BaseModel):
    document_id: str 

class ask_questionrequest(BaseModel):
    question: str
    
class read_document_request(BaseModel):
    document_id: str 


@app.get("/",tags=['Health'])
def read_root():
    return {"message": "Welcome to the PDF Upload API. Use the /upload-pdf/ endpoint to upload and read a PDF file."}



@app.post("/upload_document/",tags=['Ingester'])
async def upload_document(file: UploadFile = File(...),uploader_name: str = Form(...)):
    # Ensure the uploaded file is a PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")

    try:
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(await file.read())

        data = document_ingest(temp_file_path,file.filename,uploader_name)
        os.remove(temp_file_path)

        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the PDF: {str(e)}")


@app.post("/delete_document/",tags=['Ingester'])
async def delete_document(payload:delete_document_request):
    # Ensure the uploaded file is a PDF


    try:
        response = delete_doc(payload.document_id)
        

        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the PDF: {str(e)}")
    

@app.post("/read_document/",tags=['Ingester'])
async def read_document(payload:delete_document_request):
    # Ensure the uploaded file is a PDF


    try:
        response = read_doc(payload.document_id)
        

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the PDF: {str(e)}")
    
    
    
@app.get("/get_all_document/",tags=['Ingester'])
async def get_all_document():

    try:
        response = get_all_doc()
        

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the PDF: {str(e)}")
    
    
@app.post("/ask_question/",tags=['Retriver'])
async def ask_question(payload:ask_questionrequest):
    # Ensure the uploaded file is a PDF


    try:
        response = generate(payload.question)
        

        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the PDF: {str(e)}")