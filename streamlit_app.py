import streamlit as st
from mistralai import Mistral
import os

# Настройка страницы
st.set_page_config(
    page_title="MistralAI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Инициализация состояния сессии
if "messages" not in st.session_state:
    st.session_state.messages = []

def initialize_client():
    """Инициализация клиента MistralAI"""
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        api_key = st.secrets.get("MISTRAL_API_KEY", None)
    
    if not api_key:
        st.error("Пожалуйста, установите MISTRAL_API_KEY в secrets или переменных окружения")
        st.stop()
    
    return Mistral(api_key=api_key)

def get_chatbot_response(client, messages):
    """Получение ответа от MistralAI"""
    response = client.chat.complete(
        model="mistral-medium",  # или другая доступная модель
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

# Заголовок приложения
st.title("🤖 MistralAI Chatbot")

# Инициализация клиента
client = initialize_client()

# Отображение истории сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода пользователя
if prompt := st.chat_input("Введите ваше сообщение..."):
    # Добавление сообщения пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Получение и отображение ответа бота
    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            response = get_chatbot_response(client, st.session_state.messages)
            st.markdown(response)
    
    # Сохранение ответа бота
    st.session_state.messages.append({"role": "assistant", "content": response})

# Кнопка очистки истории
if st.sidebar.button("Очистить историю"):
    st.session_state.messages = []
    st.experimental_rerun()

# Настройки в боковой панели
st.sidebar.title("Настройки")
st.sidebar.markdown("""
### О приложении
Этот чат-бот использует API MistralAI для генерации ответов.

### Инструкции
1. Введите ваш вопрос в поле внизу
2. Дождитесь ответа бота
3. Продолжайте диалог
""")
