import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq
import datetime

# 1. БЕТТИН КОНФИГУРАЦИЯСЫ
st.set_page_config(page_title="HALIMA AI v6.0", layout="wide", page_icon="🤖")

# 2. ДИЗАЙН ЖАНА СТИЛДЕР
def local_css(style_type):
    if style_type == "agro":
        bg_color = "#f0f9f1" 
        accent = "#2e7d32"
    elif style_type == "edu":
        bg_color = "#f0f4f8" 
        accent = "#1565c0"
    else:
        bg_color = "#ffffff"
        accent = "#333333"

    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg_color}; }}
        .main-header {{ color: {accent}; font-weight: bold; font-size: 2.5rem; text-align: center; margin-bottom: 20px; }}
        .stButton>button {{ border-radius: 20px; border: 1px solid {accent}; color: {accent}; transition: 0.3s; }}
        .stButton>button:hover {{ background-color: {accent}; color: white; }}
        </style>
    """, unsafe_allow_html=True)

# 3. КООПСУЗ API ТУТАШУУ
try:
    # Ачкычтар Streamlit Secrets ичинен алынат
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("🔑 API Key ката! Streamlit Settings -> Secrets бөлүмүн текшериңиз.")
    st.stop()

# Session State инициализация
if 'auth' not in st.session_state: st.session_state.auth = False
if 'app_mode' not in st.session_state: st.session_state.app_mode = "gate"
if 'psy_chat' not in st.session_state: st.session_state.psy_chat = []
if 'user_name' not in st.session_state: st.session_state.user_name = "Конок"

# Аймактардын маалыматы
regions_data = {
    "Жалал-Абад": ["Ноокен", "Сузак", "Базар-Коргон", "Аксы", "Токтогул", "Ала-Бука"],
    "Ош": ["Кара-Суу", "Араван", "Өзгөн", "Ноокат", "Алай"],
    "Чүй": ["Аламүдүн", "Сокулук", "Жайыл", "Ысык-Ата", "Кемин"],
    "Баткен": ["Кадамжай", "Лейлек", "Баткен"],
    "Талас": ["Манас", "Бакай-Ата", "Кара-Буура", "Талас"],
    "Нарын": ["Кочкор", "Ат-Башы", "Жумгал", "Ак-Талаа"],
    "Ысык-Көл": ["Түп", "Жети-Өгүз", "Ак-Суу", "Тоң"]
}

# 4. КИРҮҮ СИСТЕМАСЫ
if not st.session_state.auth:
    local_css("default")
    st.markdown('<h1 class="main-header">🔐 HALIMA AI - Эксперттик Платформа</h1>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user = st.text_input("Колдонуучунун аты:")
        pwd = st.text_input("Пароль:", type="password")

        if st.button("Кирүү", use_container_width=True):
            if pwd == st.secrets["APP_PASSWORD"]:
                st.session_state.auth = True
                st.session_state.user_name = user if user else "Колдонуучу"
                st.rerun()
            else: 
                st.error("❌ Пароль туура эмес!")
    st.stop()

# Капталдагы меню
with st.sidebar:
    st.header(f"👤 @{st.session_state.user_name}")
    if st.button("🏠 Башкы меню", use_container_width=True):
        st.session_state.app_mode = "gate"; st.rerun()
    st.markdown("---")
    st.write(f"📅 Дата: {datetime.datetime.now().strftime('%d.%m.%Y')}")
    if st.button("🚪 Чыгуу"):
        st.session_state.auth = False; st.rerun()

# 5. БАШКЫ ТАНДОО ТЕРЕЗЕСИ
if st.session_state.app_mode == "gate":
    local_css("default")
    st.markdown(f'<h1 class="main-header">🚀 Кош келиңиз, {st.session_state.user_name}!</h1>', unsafe_allow_html=True)
    col_agro, col_edu = st.columns(2)
    with col_agro:
        st.info("🚜 **АГРОНОМИЯ ЖАНА ЭКОНОМИКА**")
        if st.button("Агрономияга өтүү", use_container_width=True):
            st.session_state.app_mode = "agro"; st.rerun()
    with col_edu:
        st.success("🎓 **БИЛИМ БЕРҮҮ ЖАНА ПСИХОЛОГИЯ**")
        if st.button("Билим берүүгө өтүү", use_container_width=True):
            st.session_state.app_mode = "edu"; st.rerun()

# --- АГРОНОМИЯ БӨЛҮМҮ ---
if st.session_state.app_mode == "agro":
    local_css("agro")
    st.markdown('<h1 class="main-header">🌿 Улуттук Агро-Экономикалык Платформа</h1>', unsafe_allow_html=True)
    agro_tabs = st.tabs(["📊 Аналитика", "💰 Сатуу", "🧪 Лаборатория", "📈 Калькулятор"])

    with agro_tabs[0]:
        col_inp, col_res = st.columns([1, 2])
        with col_inp:
            reg = st.selectbox("Облус:", list(regions_data.keys()))
            dist = st.selectbox("Район:", regions_data[reg])
            crop = st.text_input("Өсүмдүк:", "Төө буурчак")
            if st.button("🚀 Анализ"):
                with st.spinner("AI иштеп жатат..."):
                    res = client.chat.completions.create(
                        messages=[{"role":"user","content": f"{dist} районундагы {crop} боюнча агро-анализ бер."}], 
                        model="llama-3.3-70b-specdec"
                    )
                    st.session_state.agro_out = res.choices[0].message.content
        with col_res:
            if 'agro_out' in st.session_state: st.markdown(st.session_state.agro_out)

# --- БИЛИМ БЕРҮҮ БӨЛҮМҮ ---
elif st.session_state.app_mode == "edu":
    local_css("edu")
    st.markdown('<h1 class="main-header">🎓 Санариптик Билим Берүү Борбору</h1>', unsafe_allow_html=True)
    edu_tabs = st.tabs(["🛠 Сабак Пландоо", "🧠 Психолог"])

    with edu_tabs[1]:
        st.subheader("🧠 Психологдун консультациясы")
        for m in st.session_state.psy_chat:
            with st.chat_message(m["role"]): st.write(m["content"])
        
        if psy_in := st.chat_input("Жазыңыз..."):
            st.session_state.psy_chat.append({"role": "user", "content": psy_in})
            with st.chat_message("user"): st.write(psy_in)
            
            r = client.chat.completions.create(
                messages=[{"role":"system","content":"Сиз кыргыз тилдүү психологсуз."}] + st.session_state.psy_chat, 
                model="llama-3.3-70b-specdec"
            )
            resp = r.choices[0].message.content
            st.session_state.psy_chat.append({"role": "assistant", "content": resp})
            st.rerun()

st.markdown("---")
st.caption("© 2026 HALIMA AI - Маалыматтар КР Улуттук статистика комитетине негизделген.")