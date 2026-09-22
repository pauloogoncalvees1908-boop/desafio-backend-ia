import sqlite3
from contextlib import asynccontextmanager
from datetime import date
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

DB_NAME = "biblioteca.db"


def init_db():
    """Cria a tabela de livros no banco SQLite caso ela ainda não exista."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                data_publicacao TEXT NOT NULL,
                resumo TEXT NOT NULL
            )
        """)
        conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa o banco apenas quando o servidor entra em execução
    init_db()
    yield


app = FastAPI(
    title="API de Biblioteca Virtual",
    description="API para cadastro e consulta de livros com banco de dados SQLite.",
    version="1.0.0",
    lifespan=lifespan
)


# -----------------------------------------------------------------------------
# Schemas (Pydantic)
# -----------------------------------------------------------------------------
class LivroCreate(BaseModel):
    titulo: str = Field(..., json_schema_extra={"example": "Entendendo Algoritmos"})
    autor: str = Field(..., json_schema_extra={"example": "Aditya Y. Bhargava"})
    data_publicacao: date = Field(..., json_schema_extra={"example": "2017-05-01"})
    resumo: str = Field(..., json_schema_extra={"example": "Um guia ilustrado para programadores e curiosos."})


class LivroResponse(LivroCreate):
    id: int


# -----------------------------------------------------------------------------
# Endpoints da API
# -----------------------------------------------------------------------------
@app.get("/", summary="Rota Raiz", tags=["Geral"])
def home():
    return {"mensagem": "API da Biblioteca está rodando com sucesso!"}


@app.post(
    "/livros",
    response_model=LivroResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo livro",
    tags=["Livros"]
)
def cadastrar_livro(livro: LivroCreate):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO livros (titulo, autor, data_publicacao, resumo)
                VALUES (?, ?, ?, ?)
                """,
                (livro.titulo, livro.autor, str(livro.data_publicacao), livro.resumo)
            )
            conn.commit()
            livro_id = cursor.lastrowid

        livro_dict = livro.model_dump() if hasattr(livro, "model_dump") else livro.dict()
        return LivroResponse(id=livro_id, **livro_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar livro no banco de dados: {str(e)}"
        )


@app.get(
    "/livros",
    response_model=List[LivroResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar livros",
    tags=["Livros"]
)
def consultar_livros(
    titulo: Optional[str] = Query(None, description="Filtrar livros pelo título (busca parcial)"),
    autor: Optional[str] = Query(None, description="Filtrar livros pelo autor (busca parcial)")
):
    query = "SELECT id, titulo, autor, data_publicacao, resumo FROM livros WHERE 1=1"
    params = []

    if titulo:
        query += " AND titulo LIKE ?"
        params.append(f"%{titulo}%")
    if autor:
        query += " AND autor LIKE ?"
        params.append(f"%{autor}%")

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

    resultado = [
        LivroResponse(
            id=row[0],
            titulo=row[1],
            autor=row[2],
            data_publicacao=row[3],
            resumo=row[4]
        )
        for row in rows
    ]
    return resultado