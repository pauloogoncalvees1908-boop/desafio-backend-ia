import os
api_key = os.getenv("OPENAI_API_KEY")
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class ChatbotPython:
    """Chatbot especializado em responder dúvidas sobre programação Python."""

    def __init__(self, model_name: str = "gpt-4o"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "A chave de API da OpenAI não foi encontrada. "
                "Defina a variável de ambiente 'OPENAI_API_KEY'."
            )

        # Inicializa o modelo da OpenAI através do LangChain
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.2,  
            api_key=api_key
        )

       
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", (
                "Você é um tutor especialista em programação Python. "
                "Sua missão é responder às dúvidas dos usuários de forma didática, "
                "fornecendo explicações claras, exemplos práticos de código comentados "
                "e boas práticas da linguagem (PEP 8)."
            )),
            ("user", "{pergunta}")
        ])

        # Cria a cadeia de execução (LCEL - LangChain Expression Language)
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    def responder(self, pergunta: str) -> str:
        """Processa a pergunta do usuário e gera a resposta via LLM."""
        return self.chain.invoke({"pergunta": pergunta})



if __name__ == "__main__":
   
    try:
        chatbot = ChatbotPython()

        perguntas_exemplo = [
            "Como criar uma lista em Python?",
            "Qual a diferença entre uma tupla e uma lista em Python?"
        ]

        for idx, pergunta in enumerate(perguntas_exemplo, 1):
            print(f"\n{'='*20} Pergunta {idx} {'='*20}")
            print(f"Usuário: {pergunta}\n")

            resposta = chatbot.responder(pergunta)

            print("Chatbot:")
            print(resposta)
            print("-" * 50)

    except ValueError as err:
        print(f"Erro de Configuração: {err}")