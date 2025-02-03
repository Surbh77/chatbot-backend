import os

from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from langchain_openai import OpenAIEmbeddings
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from uuid import uuid4
from datetime import datetime
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Extract variables
MONGODB_ATLAS_CLUSTER_URI = os.getenv("MONGODB_ATLAS_CLUSTER_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
ATLAS_VECTOR_SEARCH_INDEX_NAME = os.getenv("ATLAS_VECTOR_SEARCH_INDEX_NAME")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

vector_store = MongoDBAtlasVectorSearch(
    collection=MONGODB_COLLECTION,
    embedding=embeddings,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine",
)

def document_loader(temp_file_path,uploader_name):

    doc_id = str(uuid4())
    loader = PyPDFLoader(temp_file_path)
    doc = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=200)
    splits = text_splitter.split_documents(doc)

    docs = [i.metadata.update({'document_id':doc_id,'uploader_name':uploader_name,'datetime':datetime.now()}) for i in splits] 
 
    return splits,doc_id

def document_ingest(file,filename,uploader_name):
    
    docs,doc_id = document_loader(file,uploader_name)
    

    uuids = [str(uuid4()) for _ in range(len(docs))]
    vector_store.add_documents(documents=docs, ids=uuids)
    
    return  {"document_name":filename, "document_id":doc_id}

def delete_doc(document_id):
    
    result = MONGODB_COLLECTION.delete_many({'document_id':document_id})
    
    return {'document_id':document_id,"remark":'Document deleted successfully'}
    
    
def read_doc(document_id):
    documents = MONGODB_COLLECTION.find({'document_id':document_id})
    doc_list = []
    for ind,document in enumerate(documents):
    
        doc_list.append([{'_id':document["_id"]},{"document_name":document["source"]},{'document_id':document["document_id"]},{'text':document["text"]}]) 
    return doc_list


def get_all_doc():
    unique_ids = MONGODB_COLLECTION.distinct("document_id")
# print(unique_ids)
    doc_dict = {} 
    doc_list = []
    for ind,i in enumerate(unique_ids):
        docu = MONGODB_COLLECTION.find({'document_id':i})
        doc_list.append({"document_id":docu[0]['document_id'],"document_name":docu[0]['source'],'uploader_name':docu[0]['uploader_name'],'datetime':docu[0]['datetime']} )
        doc_dict.update({"data":doc_list})
        
        # print(doc_dict)
    return doc_dict