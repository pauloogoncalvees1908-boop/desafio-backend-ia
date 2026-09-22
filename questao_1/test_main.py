import pytest
from fastapi.testclient import TestClient
import main
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    """Gera um banco de dados temporário isolado por teste para evitar bloqueios de arquivo no Windows."""
    test_db = tmp_path / "test_biblioteca.db"
    main.DB_NAME = str(test_db)
    main.init_db()
    yield


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"mensagem": "API da Biblioteca está rodando com sucesso!"}


def test_cadastrar_livro_sucesso():
    payload = {
        "titulo": "Entendendo Algoritmos",
        "autor": "Aditya Y. Bhargava",
        "data_publicacao": "2017-05-01",
        "resumo": "Um guia ilustrado para programadores."
    }
    response = client.post("/livros", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["titulo"] == payload["titulo"]


def test_consultar_livro_por_titulo():
    payload = {
        "titulo": "Clean Code",
        "autor": "Robert C. Martin",
        "data_publicacao": "2008-08-01",
        "resumo": "A Handbook of Agile Software Craftsmanship"
    }
    client.post("/livros", json=payload)

    response = client.get("/livros?titulo=Clean")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["titulo"] == "Clean Code"


def test_consultar_livro_por_autor():
    payload = {
        "titulo": "Refactoring",
        "autor": "Martin Fowler",
        "data_publicacao": "1999-07-08",
        "resumo": "Improving the Design of Existing Code"
    }
    client.post("/livros", json=payload)

    response = client.get("/livros?autor=Fowler")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["autor"] == "Martin Fowler"