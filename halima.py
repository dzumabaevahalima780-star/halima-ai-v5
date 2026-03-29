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

# 1. Негизги жөндөөлөр
st.set_page_config(page_title="HALIMA AI v7.0", layout="wide", page_icon="🤖")

# 2. Файлдарды окуу функциясы
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
    except:
        return "Файлды окууда ката кетти."

# 3. Стильдер
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

# 4. API Ключ
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Key ката!")
    st.stop()

# Сессияларды сактоо
if 'auth' not in st.session_state: st.session_state.auth = False
if 'app_mode' not in st.session_state: st.session_state.app_mode = "gate"
if 'psy_chat' not in st.session_state: st.session_state.psy_chat = []

# Аймактар маалыматы
regions_data = {
    "Жалал-Абад": ["Ноокен", "Сузак", "Базар-Коргон", "Аксы", "Токтогул", "Ала-Бука"],
    "Ош": ["Кара-Суу", "Араван", "Өзгөн", "Ноокат", "Алай"],
    "Чүй": ["Аламүдүн", "Сокулук", "Жайыл", "Ысык-Ата", "Кемин"],
    "Баткен": ["Кадамжай", "Лейлек", "Баткен"],
    "Талас": ["Манас", "Бакай-Ата", "Кара-Буура", "Талас"],
    "Нарын": ["Кочкор", "Ат-Башы", "Жумгал", "Ак-Талаа"],
    "Ысык-Көл": ["Түп", "Жети-Өгүз", "Ак-Суу", "Тоң"]
}

# 5. КИРҮҮ (Пароль: 31012008)
if not st.session_state.auth:
    st.title("🔐 HALIMA AI - Эксперттик Платформа")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user = st.text_input("Колдонуучунун аты:")
        pwd = st.text_input("Пароль:", type="password")
        if st.button("Кирүү"):
            if pwd == "31012008":
                st.session_state.auth = True
                st.session_state.user_name = user
                st.rerun()
            else: st.error("Пароль туура!")
    st.stop()

# 6. БАШКЫ МЕНЮ
if st.session_state.app_mode == "gate":
    st.markdown('<h1 class="main-header">🚀 Кош келиңиз!</h1>', unsafe_allow_html=True)
    col_agro, col_edu = st.columns(2)
    with col_agro:
        st.info("🚜 **АГРОНОМИЯ ЖАНА ЭКОНОМИКА**")
        if st.button("Агрономияга өтүү"):
            st.session_state.app_mode = "agro"; st.rerun()
    with col_edu:
        st.success("🎓 **БИЛИМ БЕРҮҮ ЖАНА ПСИХОЛОГИЯ**")
        if st.button("Билим берүүгө өтүү"):
            st.session_state.app_mode = "edu"; st.rerun()
    st.stop()

# 7. ИШТӨӨ БӨЛҮМДӨРҮ
local_css(st.session_state.app_mode)
with st.sidebar:
    st.header(f"👤 @{st.session_state.user_name}")
    if st.button("🏠 Башкы меню"):
        st.session_state.app_mode = "gate"; st.rerun()
    st.write(f"📅 {datetime.datetime.now().strftime('%d.%m.%Y')}")

# --- АГРОНОМИЯ БӨЛҮМҮ ---
if st.session_state.app_mode == "agro":
    st.markdown('<h1 class="main-header">🌿 Агро-Экономикалык Платформа</h1>', unsafe_allow_html=True)
    
    # ФОТО АНАЛИЗ ЖАНА ФАЙЛ (ЖАҢЫ)
    with st.expander("📸 Сүрөт же Анализ файлын жүктөө (ЖАҢЫ)"):
        up_file = st.file_uploader("Файлды тандаңыз", type=['pdf', 'docx', 'jpg', 'png'], key="agro_up")
        if up_file:
            if up_file.type.startswith('image'):
                st.image(up_file, width=300)
                if st.button("🖼️ Сүрөттү AI менен талда"):
                    res = client.chat.completions.create(messages=[{"role":"user","content":"Сүрөттү кыргызча талда."}], model="llama-3.2-11b-vision-preview")
                    st.info(res.choices[0].message.content)
            else:
                text = extract_text_from_file(up_file)
                if st.button("🔍 Файлды талда"):
                    res = client.chat.completions.create(messages=[{"role":"user","content":f"Текстти талда: {text[:2000]}"}], model="llama-3.1-8b-instant")
                    st.info(res.choices[0].message.content)

    tabs = st.tabs(["📊 Аналитика", "💰 Сатуу Каналдары", "📈 Калькулятор"])
    with tabs[0]:
        reg = st.selectbox("Облус:", list(regions_data.keys()))
        dist = st.selectbox("Район:", regions_data[reg])
        crop = st.text_input("Өсүмдүк:", "Төө буурчак")
        if st.button("🚀 Анализди баштоо"):
            res = client.chat.completions.create(messages=[{"role":"user","content":f"{dist} районунда {crop} өстүрүү боюнча кеңеш бер."}], model="llama-3.1-8b-instant")
            st.write(res.choices[0].message.content)

# --- БИЛИМ БЕРҮҮ БӨЛҮМҮ ---
elif st.session_state.app_mode == "edu":
    st.markdown('<h1 class="main-header">🎓 Санариптик Билим Борбору</h1>', unsafe_allow_html=True)
    
    # ФАЙЛДАРДЫ ТАЛДОО (ЖАҢЫ)
    with st.expander("📄 Документти талдоо (PDF/DOCX)"):
        edu_file = st.file_uploader("Сабак планын же текстти жүктөңүз", type=['pdf', 'docx', 'txt'], key="edu_up")
        if edu_file:
            text = extract_text_from_file(edu_file)
            if st.button("🔍 Документти AI менен талда"):
                res = client.chat.completions.create(messages=[{"role":"user","content":f"Төмөнкү документти кыргызча мазмундап бер: {text[:2000]}"}], model="llama-3.1-8b-instant")
                st.info(res.choices[0].message.content)

    tabs = st.tabs(["🛠 Сабак Конструктору", "🎯 Профориентация", "🧠 Психолог"])
    with tabs[0]:
        topic = st.text_input("Сабактын темасы:")
        if st.button("План түзүү"):
            res = client.chat.completions.create(messages=[{"role":"user","content":f"{topic} темасына сабак планы."}], model="llama-3.1-8b-instant")
            st.write(res.choices[0].message.content)
            
    with tabs[2]:
        st.subheader("🧠 Психологдун консультациясы")
        for m in st.session_state.psy_chat:
            with st.chat_message(m["role"]): st.write(m["content"])
        if p_in := st.chat_input("Суроо жазыңыз..."):
            st.session_state.psy_chat.append({"role": "user", "content": p_in})
            r = client.chat.completions.create(messages=[{"role":"system","content":"Сиз психологсуз."}] + st.session_state.psy_chat, model="llama-3.1-8b-instant")
            st.session_state.psy_chat.append({"role": "assistant", "content": r.choices[0].message.content})
            st.rerun()

st.markdown("---")
st.caption("© 2026 HALIMA AI v7.0")