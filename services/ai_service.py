from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def gerar_explicacao(
    enunciado,
    resposta
):

    prompt = f"""
    Explique porque esta resposta está correta.

    Questão:
    {enunciado}

    Resposta correta:
    {resposta}

    Gere uma explicação curta e didática.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content