import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq
import datetime
from PIL import Image
import PyPDF2
import docx
import io

# 1. Баракчанын негизги жөндөөлөрү
st.set_page_config(page_title="HALIMA AI v7.0", layout="wide", page_icon="🤖")

# 2. Файлдардан (PDF, DOCX, TXT) текстти окуу функциясы
def extract_text_from_file(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            return "".join([page.extract_text() for page in pdf_reader.pages])
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            return str(uploaded_file.read(), "utf-8")
    except Exception as e:
        return f"Файлды окууда ката кетти: {e}"

# 3. Визуалдык стильдер
def local_css(style_type):
    bg_color = "#f0f9f1" if style_type == "agro" else "#f0f4f8"
    accent = "#2e7d32" if style_type == "agro" else "#1565c0"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg_color}; }}
        .main-header {{ color: {accent}; font-weight: bold; font-size: 2.5rem; }}
        .stButton>button {{ border-radius: 20px; border: 1px solid {accent}; color: {accent}; width: 100%; }}
        </style>
    """, unsafe_allow_html=True)

# 4. API Ключту текшерүү
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Key ката! .streamlit/secrets.toml файлын текшериңиз.")
    st.stop()

# 5. Сессияны башкаруу
if 'auth' not in st.session_state: st.session_state.auth = False
if 'app_mode' not in st.session_state: st.session_state.app_mode = "gate"
if 'user_name' not in st.session_state: st.session_state.user_name = "Конок"

# 6. КИРҮҮ БЕТИ (Авторизация)
if not st.session_state.auth:
    st.title("🔐 HALIMA AI - Эксперттик Платформа")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user = st.text_input("Колдонуучунун аты:")
        pwd = st.text_input("Пароль:", type="password")
        if st.button("Кирүү"):
            if pwd == "31012008": # Сиз сураган жаңы пароль
                st.session_state.auth = True
                st.session_state.user_name = user
                st.rerun()
            else:
                st.error("Пароль туура эмес!")
    st.stop()

# 7. БАШКЫ МЕНЮ
if st.session_state.app_mode == "gate":
    st.markdown('<h1 class="main-header">🚀 Кош келиңиз, Кожоюн!</h1>', unsafe_allow_html=True)
    col_agro, col_edu = st.columns(2)
    with col_agro:
        st.info("🚜 **АГРОНОМИЯ**\n\nФото анализ жана экономикалык эсептөөлөр.")
        if st.button("Агрономияга өтүү"):
            st.session_state.app_mode = "agro"; st.rerun()
    with col_edu:
        st.success("🎓 **БИЛИМ БЕРҮҮ**\n\nДокументтерди талдоо жана психолог кеңеши.")
        if st.button("Билим берүүгө өтүү"):
            st.session_state.app_mode = "edu"; st.rerun()
    st.stop()

# 8. ИШТӨӨ БӨЛҮМДӨРҮ
local_css(st.session_state.app_mode)

with st.sidebar:
    st.header(f"👤 @{st.session_state.user_name}")
    if st.button("🏠 Башкы менюга кайтуу"):
        st.session_state.app_mode = "gate"; st.rerun()
    st.write(f"📅 {datetime.datetime.now().strftime('%d.%m.%Y')}")

st.markdown(f'<h1 class="main-header">{"🌿 Агро-Эксперт" if st.session_state.app_mode == "agro" else "🎓 Билим Борбору"}</h1>', unsafe_allow_html=True)

# 9. ЖАҢЫ ФУНКЦИЯ: ФОТО ЖАНА ФАЙЛ АНАЛИЗИ
st.markdown("---")
st.subheader("📸 Сүрөт же Файл аркылуу анализ")
uploaded_file = st.file_uploader("Өсүмдүктүн сүрөтүн же анализ файлын жүктөңүз", type=['png', 'jpg', 'jpeg', 'pdf', 'docx', 'txt'])

if uploaded_file:
    if uploaded_file.type.startswith('image'):
        # Сүрөттү иштетүү
        image = Image.open(uploaded_file)
        st.image(image, caption='Жүктөлгөн сүрөт', use_container_width=True)
        
        if st.button("🖼️ Сүрөттү AI менен талда"):
            with st.spinner("Халима сүрөттү көрүп жатат..."):
                # Vision моделин колдонуу
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": "Бул сүрөттөгү абалды кыргыз тилинде эксперт катары деталдуу талдап бер."}],
                    model="llama-3.2-11b-vision-preview"
                )
                st.write("### 🤖 Халиманын анализи:")
                st.write(res.choices[0].message.content)
    else:
        # Файлды иштетүү
        file_text = extract_text_from_file(uploaded_file)
        st.success("📄 Файл ийгиликтүү окулду!")
        if st.button("🔍 Документтин мазмунун талда"):
            with st.spinner("Текст талданууда..."):
                # Тексттик модель
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Төмөнкү текстти кыргыз тилинде кыскача мазмундап жана эксперттик корутунду бер: {file_text[:3000]}"}],
                    model="llama-3.1-8b-instant"
                )
                st.write("### 🤖 Документ боюнча корутунду:")
                st.write(res.choices[0].message.content)

st.markdown("---")
st.caption("© 2026 HALIMA AI - Жаңыланган версия v7.0")