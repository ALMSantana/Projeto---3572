from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4"

def carrega(nome_do_arquivo):
    try:
        with open(nome_do_arquivo, "r") as arquivo:
            dados = arquivo.read()
            return dados
    except IOError as e:
        print(f"Erro no carregamento de arquivo: {e}")

def salva(nome_do_arquivo, conteudo):
    try:
        with open(nome_do_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)
    except IOError as e:
        print(f"Erro ao salvar arquivo: {e}")


def analisar_transacao(lista_transacoes):
    print("1.Executando a análise de transação")

    prompt_sistema = """
    Analise as transações financeiras a seguir e identifique se cada uma delas é uma "Possível Fraude" ou deve ser "Aprovada". 
    Adicione um atributo "Status" com um dos valores: "Possível Fraude" ou "Aprovado".

    Cada nova transação deve ser inserida dentro da lista do JSON. 

    # Possíveis indicações de fraude
    - Transações com valores muito discrepantes
    - Transações que ocorrem em locais muito distantes um do outro

    Adote o formato de resposta abaixo para compor sua resposta.
    
    # Formato Saída 
    {
        "transacoes": [
            {
            "id": "id",
            "tipo": "crédito ou débito",
            "estabelecimento": "nome do estabelecimento",
            "horário": "horário da transação",
            "valor": "R$XX,XX",
            "nome_produto": "nome do produto",
            "localização": "cidade - estado (País)"
            "status": ""
            },
        ]
    } 
    """

    lista_mensagens = [
        {
            "role": "system",
            "content": prompt_sistema
        },
        {
            "role": "user",
            "content": f"Considere o CSV abaixo, onde cada linha é uma transação diferente: {lista_transacoes}. Sua resposta deve adotar o #Formato de Resposta (apenas um json sem outros comentários)"
        }
    ]

    resposta = cliente.chat.completions.create(
        messages = lista_mensagens,
        model=modelo,
        temperature=0
    )

    conteudo = resposta.choices[0].message.content.replace("'", '"')
    print("\Conteúdo:", conteudo)
    json_resultado = json.loads(conteudo)
    print("\nJSON:", json_resultado)
    return json_resultado

def gerar_parecer(transacao):
    print("2. Gerando um parecer para cada transação")

    prompt_sistema = f"""
    Para a seguinte transação, forneça um parecer, apenas se o status dela for de "Possível Fraude". Indique no parecer uma justificativa para que você identifique uma fraude.
    Transação: {transacao}

    ## Formato de Resposta
    "id": "id",
    "tipo": "crédito ou débito",
    "estabelecimento": "nome do estabelecimento",
    "horario": "horário da transação",
    "valor": "R$XX,XX",
    "nome_produto": "nome do produto",
    "localizacao": "cidade - estado (País)"
    "status": "",
    "parecer" : "Colocar Não Aplicável se o status for Aprovado"
    """

    lista_mensagens = [
        {
            "role": "user",
            "content": prompt_sistema
        }
    ]

    resposta = cliente.chat.completions.create(
        messages = lista_mensagens,
        model=modelo,
    )

    conteudo = resposta.choices[0].message.content
    print("Finalizou a geração de parecer")
    return conteudo




lista_de_transacoes = carrega("transacoes.csv")
print(analisar_transacao(lista_de_transacoes))
transacoes_analisadas = analisar_transacao(lista_de_transacoes)

for uma_transacao in transacoes_analisadas["transacoes"]:
    if uma_transacao["status"] == "Possível Fraude":
        um_parecer = gerar_parecer(uma_transacao)
        print(um_parecer)
