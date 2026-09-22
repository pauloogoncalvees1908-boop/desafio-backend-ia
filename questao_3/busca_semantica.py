from typing import List, Dict, Any
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


class SistemaBuscaSemantica:
    """Sistema de indexação e busca semântica em documentos de texto utilizando FAISS."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Inicializa o modelo de embeddings.
        O modelo 'all-MiniLM-L6-v2' gera vetores densos de 384 dimensões.
        """
        print(f"Carregando modelo de embeddings: {model_name}...")
        self.encoder = SentenceTransformer(model_name)
        self.dimension = self.encoder.get_sentence_embedding_dimension()
        
       
        self.index = faiss.IndexFlatIP(self.dimension)
        self.documentos: List[Dict[str, Any]] = []

    def adicionar_documentos(self, docs: List[Dict[str, str]]):
        """
        Gera embeddings para a lista de documentos e armazena no FAISS.
        
        Cada item de 'docs' deve conter ao menos a chave 'conteudo'.
        """
        self.documentos.extend(docs)
        textos = [doc["conteudo"] for doc in docs]

        embeddings = self.encoder.encode(textos, convert_to_numpy=True, show_progress_bar=False)


        faiss.normalize_L2(embeddings)


        self.index.add(embeddings.astype(np.float32))
        print(f"{len(docs)} documentos indexados com sucesso na Vector Store!")

    def buscar(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Realiza a busca semântica para uma determinada consulta.
        Retorna os 'top_k' documentos mais similares e seus respectivos scores.
        """

        query_embedding = self.encoder.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)


        scores, indices = self.index.search(query_embedding.astype(np.float32), top_k)

        resultados = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:  # Garante um índice válido
                resultados.append({
                    "score_similaridade": float(score),
                    "documento": self.documentos[idx]
                })

        return resultados



if __name__ == "__main__":

    base_conhecimento = [
        {
            "id": 1,
            "titulo": "Introdução ao FastAPI",
            "conteudo": "FastAPI é um framework moderno em Python para construir APIs com alta performance baseadas em Pydantic e Type Hints."
        },
        {
            "id": 2,
            "titulo": "Banco de Dados Relacionais",
            "conteudo": "PostgreSQL e MySQL são sistemas de gerenciamento de banco de dados relacionais que utilizam a linguagem SQL para consultas estruturadas."
        },
        {
            "id": 3,
            "titulo": "Inteligência Artificial Generativa",
            "conteudo": "Modelos de linguagem como GPT e Claude utilizam a arquitetura Transformer para processar textos e gerar respostas coerentes."
        },
        {
            "id": 4,
            "titulo": "Vector Stores na Prática",
            "conteudo": "FAISS e ChromaDB permitem armazenar e buscar embeddings com alta eficiência para aplicações RAG."
        }
    ]


    busca_engine = SistemaBuscaSemantica()
    busca_engine.adicionar_documentos(base_conhecimento)


    consultas_teste = [
        "Como criar APIs rápidas em Python?",
        "Ferramentas para armazenar vetores de IA"
    ]

    for q in consultas_teste:
        print(f"\n==================================================")
        print(f"Consulta: '{q}'")
        print("==================================================")
        
        resultados = busca_engine.buscar(query=q, top_k=2)

        for i, res in enumerate(resultados, 1):
            doc = res["documento"]
            score = res["score_similaridade"]
            print(f"Resultado #{i} | Similaridade: {score:.4f}")
            print(f"Título: {doc['titulo']}")
            print(f"Conteúdo: {doc['conteudo']}\n")