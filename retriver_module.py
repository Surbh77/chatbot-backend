import os

from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from langchain_openai import OpenAIEmbeddings
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from uuid import uuid4
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Extract variables
MONGODB_ATLAS_CLUSTER_URI = os.getenv("MONGODB_ATLAS_CLUSTER_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
ATLAS_VECTOR_SEARCH_INDEX_NAME = os.getenv("ATLAS_VECTOR_SEARCH_INDEX_NAME")




llm = ChatOpenAI(model="gpt-4o-mini")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

vector_store = MongoDBAtlasVectorSearch(
    collection=MONGODB_COLLECTION,
    embedding=embeddings,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine",
)



def retrieve(query):
    results = vector_store.similarity_search(
    query
    )
    return results


def generate(query):
    
    retrived_content = retrieve(query)
    
    docs_content = "\n\n".join(doc.page_content for doc in retrived_content)
    metedata = [i.metadata for i in retrived_content]
    
    template = ChatPromptTemplate([
        ("system", """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
        Strictly dont't give answer if the question is not related to the provided context
        Question: {question} 
        Context: {context} 
        Answer:"""),
    ])


    
    # messages = prompt.invoke({"question": query, "context": docs_content})
    messages = template.invoke({"question": query, "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content,"question_id":str(uuid4()),"metedata":metedata,"content":docs_content}

