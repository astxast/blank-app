import streamlit as st
from mistralai import Mistral
import os
import PyPDF2
import io
from docx import Document

# Настройка страницы
st.set_page_config(
    page_title="MistralAI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Список доступных моделей
AVAILABLE_MODELS = {
    "Mistral Large": "mistral-large-latest",
    "Pixtral Large": "pixtral-large-latest",
    "Mistral Moderation": "mistral-moderation-latest",
    "Ministral 3B": "ministral-3b-latest",
    "Ministral 8B": "ministral-8b-latest",
    "Open Mistral Nemo": "open-mistral-nemo",
    "Mistral Small": "mistral-small-latest",
    "Codestral": "codestral-latest"
}

# Инициализация состояния сессии
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "mistral-large-latest"

def initialize_client():
    """Инициализация клиента MistralAI"""
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        api_key = st.secrets.get("MISTRAL_API_KEY", None)
    
    if not api_key:
        st.error("Пожалуйста, установите MISTRAL_API_KEY в secrets или переменных окружения")
        st.stop()
    
    return Mistral(api_key=api_key)

def read_pdf(file):
    """Чтение содержимого PDF файла"""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def read_docx(file):
    """Чтение содержимого DOCX файла"""
    doc = Document(file)
    text = []
    for paragraph in doc.paragraphs:
        if paragraph.text:
            text.append(paragraph.text)
    return '\n'.join(text)

def read_text_file(file):
    """Чтение содержимого текстового файла"""
    return file.getvalue().decode('utf-8')

def get_file_content(uploaded_file):
    """Получение содержимого файла в зависимости от его типа"""
    if uploaded_file.type == "application/pdf":
        return read_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return read_docx(uploaded_file)
    else:  # Предполагаем, что это текстовый файл
        return read_text_file(uploaded_file)

def get_chatbot_response(client, messages):
    """Получение ответа от MistralAI"""
    response = client.chat.complete(
        model=st.session_state.selected_model,
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content

def analyze_file_content(client, content, question=None):
    """Анализ содержимого файла"""
    if question:
        prompt = f"Проанализируй следующий текст и ответь на вопрос: {question}\n\nТекст:\n{content[:6000]}"
    else:
        prompt = f"Проанализируй следующий текст и предоставь краткое содержание основных моментов:\n\n{content[:6000]}"
    
    messages = [{"role": "user", "content": prompt}]
    return get_chatbot_response(client, messages)

# Заголовок приложения
st.title("🤖 MistralAI Chatbot с анализом файлов")

# Инициализация клиента
client = initialize_client()

# Настройки в боковой панели
st.sidebar.title("Настройки")

# Выбор модели
selected_model_name = st.sidebar.selectbox(
    "Выберите модель",
    list(AVAILABLE_MODELS.keys()),
    format_func=lambda x: x,
    help="Выберите модель Mistral AI для генерации ответов"
)
st.session_state.selected_model = AVAILABLE_MODELS[selected_model_name]

# Информация о текущей модели
st.sidebar.info(f"Выбрана модель: {st.session_state.selected_model}")

# Загрузка файла
st.sidebar.title("Загрузка файла")
uploaded_file = st.sidebar.file_uploader(
    "Загрузите файл для анализа",
    type=['txt', 'pdf', 'docx'],
    help="Поддерживаются файлы форматов TXT, PDF и DOCX"
)

# Если файл загружен
if uploaded_file:
    with st.sidebar:
        st.write("Файл загружен:", uploaded_file.name)
        question = st.text_input("Введите вопрос по содержимому файла (необязательно)")
        if st.button("Анализировать файл"):
            with st.spinner("Читаю файл..."):
                content = get_file_content(uploaded_file)
                
            with st.spinner("Анализирую содержимое..."):
                analysis = analyze_file_content(client, content, question)
                
                # Добавляем результат анализа в историю сообщений
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"Проанализируй файл {uploaded_file.name}" + 
                              (f" и ответь на вопрос: {question}" if question else "")
                })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": analysis
                })
                st.experimental_rerun()

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

# Дополнительная информация в боковой панели
st.sidebar.markdown("""
### О приложении
Этот чат-бот использует API MistralAI для генерации ответов и анализа файлов.

### Поддерживаемые форматы файлов
- TXT (текстовые файлы)
- PDF документы
- DOCX документы

### Инструкции
1. Выберите нужную модель Mistral AI
2. Загрузите файл через боковую панель (по желанию)
3. Задайте вопрос по содержимому файла (по желанию)
4. Нажмите "Анализировать файл" или задайте вопрос в чате
5. Дождитесь ответа бота
""")
