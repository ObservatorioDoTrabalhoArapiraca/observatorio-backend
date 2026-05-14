# rodar o projeto: uvicorn api.index:app --reload
# source /home/usuario/Github/observatorio-fast-api/.venv/bin/activate && uvicorn api.index:app --reload --port 8001
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

from .core.referenciaisSchemas import MovimentacoesSchema
from fastapi import FastAPI, Depends
from .core.database import get_db
from .core.routers import analises, referenciais, analisesrais
from .core.routers import pdfs

from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware


# 4. Inicialização do App
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://observatorio-arapiraca.vercel.app", 
        "http://localhost:5173", 
        "http://127.0.0.1:5173"
        ], # Em produção, trocaremos pelo link da Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Função para pegar a conexão com o banco 

@app.get("/")
def root():
    return {"message": "API do Observatório rodando!"}

@app.get("/api/teste")
def teste():
    return {"status": "ok"}
# @app.get("/api/movimentacoes", response_model=List[MovimentacoesSchema])
# def get_movimentacoes(db: Session = Depends(get_db)):
#   return MovimentacaoRepository.get_movimentacoes(db)

app.include_router(referenciais.router, prefix="/api")
app.include_router(analises.router, prefix="/api")
app.include_router(analisesrais.router, prefix="/api")
app.include_router(pdfs.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.index:app", host="0.0.0.0", port=8001, reload=True)