
import os
from langchain_openai import ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType
from langchain_experimental.tools import PythonREPLTool

from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("No se encontró la variable de entorno OPENAI_API_KEY. Por favor, configúrala.")

def llm_response():

    llm = ChatOpenAI(temperature=0, api_key=api_key)

    tools = [PythonREPLTool()]

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    while True:
        try:
            # Solicitar entrada del usuario
            print("¡Hola! Soy un asistente de IA que puede escribir y ejecutar código Python.")
            print("Escribe 'salir' para terminar.")
            
            user_input = input("\nPregunta: ")


            if user_input.lower() == 'salir':
                print("¡Hasta luego!")
                break

            # El agente ejecuta la tarea basándose en la entrada del usuario
            response = agent.invoke(user_input)

            # Imprimir la respuesta final del agente
            print("\nRespuesta:")
            print(response.get('output', 'No se pudo obtener una respuesta.'))

        except Exception as e:
            print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    llm_response()