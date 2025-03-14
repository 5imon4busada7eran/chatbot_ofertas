from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)

import openai
from streamlit_chat import message
from utils import *


from dotenv import load_dotenv
import os


import streamlit as st

# Define las variables de entorno y otros secrets


class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

    def __repr__(self):
        return f"Document(page_content='{self.page_content}', metadata={self.metadata})"

    __str__ = __repr__


st.markdown("<h2 style='text-align: center;'>Experto en Diseño de Mercados de Ofertas</h2>", unsafe_allow_html=True)

st.markdown(
    """
    <img src="https://www.colbun.cl/resourcePackages/colbunweb/assets/dist/images/header/logo.png" width="100" align="middle">
    """,
    unsafe_allow_html=True,
)

#st.markdown("<h6 style='text-align: center;'>Creado por: Robinson Cornejo</h6>", unsafe_allow_html=True)


# URL of your custom logo
#custom_logo_url = "https://www.colbun.cl/resourcePackages/colbunweb/assets/dist/images/header/logo.png"

# Initialize session states if they don't exist
if 'responses' not in st.session_state:
    st.session_state['responses'] = ["Hola, soy experto en el diseño de mercados de ofertas y tengo todos los informes de ECCO International y Vinken-Dictuc en mis conocimientos, ¿En qué puedo ayudarte hoy?"]

if 'requests' not in st.session_state:
    st.session_state['requests'] = []

# # Display a chat-like message with a custom logo
# col1, col2 = st.columns([1, 5])  # Adjust the ratio based on your design needs
# with col1:
#     st.image(custom_logo_url, width=100)  # Adjust the width as needed to fit your layout
# with col2:
#     st.write(st.session_state['responses'][0])
    
llm = ChatOpenAI(model_name="gpt-4", openai_api_key=OPENAI_API_KEY)

if 'buffer_memory' not in st.session_state:
            st.session_state.buffer_memory=ConversationBufferWindowMemory(k=3,return_messages=True)


# system_msg_template = SystemMessagePromptTemplate.from_template(
#     template="""Responda la pregunta con la mayor veracidad posible utilizando el contexto proporcionado,
# y si la respuesta no está contenida en el texto a continuación, diga 'Podrias preguntarle al equipo de Trading, seguramente ellos podran orientarte' """)

system_msg_template = SystemMessagePromptTemplate.from_template(
    template="""Responde la pregunta con la mayor veracidad posible utilizando el contexto proporcionado. 
    Si no conoce la respuesta, iterar dos veces para pedir más detalles.
Preguntar siempre si el usuario está satisfecho con la respuesta.
Iterar hasta tres veces si el usuario no está satisfecho.
Proporcionar fuentes al final de cada respuesta. 
Al final de tu respuesta, sugiere correlaciones con otros documentos de la misma temática.
Cuando el usuario lo pida, ofrece la mejor recomendación basada en tu conocimiento general de los diseños de mercados basados en ofertas y mejores prácticas en la industria, 
    incluyendo nuevas ideas y propuestas que puedan ser beneficiosas. Solo si no puedes ofrecer ninguna recomendación útil, entonces sugiere al usuario que 
    'Podrías preguntarle al equipo de Trading, seguramente ellos podrán orientarte'.""")

human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")

prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

conversation = ConversationChain(memory=st.session_state.buffer_memory, prompt=prompt_template, llm=llm, verbose=True)




# container for chat history
response_container = st.container()
# container for text box
textcontainer = st.container()


with textcontainer:
    query = st.text_input("Consulta: ", key="input")
    if query:
        with st.spinner("Escribiendo..."):
            conversation_string = get_conversation_string()
            st.code(conversation_string)
            #user_entities = extract_entities(query)
            #print("#######")
            #print(user_entities)
            refined_query = query_refiner(conversation_string, query)
            #st.subheader("Refined Query:")
            #st.write(refined_query)
            context = get_answer(refined_query)
            print(context)  
            response = conversation.predict(input=f"Context:\n {context} \n\n Query:\n{query}")
        st.session_state.requests.append(query)
        st.session_state.responses.append(response) 
with response_container:
    if st.session_state['responses']:

        for i in range(len(st.session_state['responses'])):
            message(st.session_state['responses'][i],key=str(i))
            if i < len(st.session_state['requests']):
                message(st.session_state["requests"][i], is_user=True,key=str(i)+ '_user')

