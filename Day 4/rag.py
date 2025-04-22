from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

pdf_path = (__file__).parent / "nodejs.pdf" 

loader = PyPDFLoader(file_path=pdf_path)

docs = loader.load()