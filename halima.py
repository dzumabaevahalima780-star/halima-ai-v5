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
import base64

# 1. Негизги жөндөөлөр
st.set_page_config(page_title="HALIMA AI v7.0", layout="wide", page_icon="🤖")

def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

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
    except Exception:
        return "Файлды окууда ката кетти."

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
except Exception:
    st.error("API Key ката! .streamlit/secrets.toml файлын текшериңиз.")
    st.stop()

if 'auth' not in st.session_state: st.session_state.auth = False
if 'app_mode' not in st.session_state: st.session_state.app_mode = "gate"
if 'psy_chat' not in st.session_state: st.session_state.psy_chat = []

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
            else:
                st.error("Пароль туура эмес!")
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

local_css(st.session_state.app_mode)
with st.sidebar:
    st.header(f"👤 @{st.session_state.user_name}")
    if st.button("🏠 Башкы меню"):
        st.session_state.app_mode = "gate"; st.rerun()
    st.write(f"📅 {datetime.datetime.now().strftime('%d.%m.%Y')}")

# --- АГРОНОМИЯ БӨЛҮМҮ ---
if st.session_state.app_mode == "agro":
    st.markdown('<h1 class="main-header">🌿 Агро-Экономикалык Платформа</h1>', unsafe_allow_html=True)
    
    with st.expander("📸 Сүрөт же Анализ файлын жүктөө"):
        up_file = st.file_uploader("Файлды тандаңыз", type=['pdf', 'docx', 'jpg', 'png'], key="agro_up")
        if up_file:
            user_task = st.text_area("AI үчүн тапшырма жазыңыз:", placeholder="Мисалы: Бул сүрөттөгү ооруну аныкта...")
            if up_file.type.startswith('image'):
                st.image(up_file, width=300)
                if st.button("🖼️ Сүрөттү AI менен талда"):
                    base64_image = encode_image(up_file)
                    final_prompt = user_task if user_task else "Бул сүрөттөгү агро-ситуацияны кыргызча талдап бер."
                    try:
                        res = client.chat.completions.create(
                            messages=[{
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": final_prompt},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ]
                            }],
                            model="llama-3.2-11b-vision-instant" # Жаңыланган модель
                        )
                        st.info(res.choices[0].message.content)
                    except Exception as e:
                        st.error(f"Ката кетти: {e}")
            else:
                text = extract_text_from_file(up_file)
                if st.button("🔍 Файлды талда"):
                    prompt = f"Тапшырма: {user_task}\n\nТекст: {text[:2000]}" if user_task else f"Текстти талда: {text[:2000]}"
                    res = client.chat.completions.create(messages=[{"role":"user","content": prompt}], model="llama-3.1-8b-instant")
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
    
    with st.expander("📄 Документти талдоо (PDF/DOCX)"):
        edu_file = st.file_uploader("Документти жүктөңүз", type=['pdf', 'docx', 'txt'], key="edu_up")
        if edu_file:
            edu_task = st.text_area("Документ боюнча тапшырма:", placeholder="Мисалы: Тест түз же кыскарт...")
            text = extract_text_from_file(edu_file)
            if st.button("🔍 Документти AI менен талда"):
                prompt = f"Тапшырма: {edu_task}\n\nТекст: {text[:2000]}" if edu_task else f"Мазмундап бер: {text[:2000]}"
                res = client.chat.completions.create(messages=[{"role":"user","content": prompt}], model="llama-3.1-8b-instant")
                st.info(res.choices[0].message.content)

    tabs = st.tabs(["🛠 Сабак Конструктору", "🎯 Профориентация", "🧠 Психолог"])
    
    with tabs[0]:
        topic = st.text_input("Сабактын темасы:")
        if st.button("План түзүү"):
            res = client.chat.completions.create(messages=[{"role":"user","content":f"{topic} темасына сабак планы."}], model="llama-3.1-8b-instant")
            st.write(res.choices[0].message.content)

    with tabs[1]:
        st.subheader("🎯 Голланд методикасы боюнча кесип тандоо")
        with st.form("holland_test"):
            c1 = st.slider("Реалдуу (Техника, жабдыктар менен иштөө):", 0, 10, 5)
            c2 = st.slider("Интеллектуалдык (Илим, изилдөө):", 0, 10, 5)
            c3 = st.slider("Артисттик (Чыгармачылык, дизайн):", 0, 10, 5)
            c4 = st.slider("Социалдык (Адамдарга жардам берүү, окутуу):", 0, 10, 5)
            c5 = st.slider("Предпринимателдик (Бизнес, лидерлик):", 0, 10, 5)
            c6 = st.slider("Конвенционалдык (Эсеп-кысап, документтер):", 0, 10, 5)
            submit = st.form_submit_button("Жыйынтыкты көрүү")
        
        if submit:
            scores = {"Реалдуу": c1, "Интеллектуалдык": c2, "Артисттик": c3, "Социалдык": c4, "Бизнес": c5, "Офис": c6}
            fig = go.Figure(data=go.Scatterpolar(r=list(scores.values()), theta=list(scores.keys()), fill='toself'))
            st.plotly_chart(fig)
            
            top_type = max(scores, key=scores.get)
            st.success(f"Сиздин басымдуу тибиңиз: **{top_type}**")
            
            # AI сунушу
            with st.spinner("Университеттер жана кесиптер тандалууда..."):
                res = client.chat.completions.create(
                    messages=[{"role":"user","content": f"Голланд тести боюнча {top_type} тибиндеги окуучуга Кыргызстандагы 5 кесипти жана аларды окуткан эң мыкты университеттерди тизмелеп бер."}],
                    model="llama-3.1-8b-instant"
                )
                st.write(res.choices[0].message.content)
            
    with tabs[2]:
        st.subheader("🧠 Психологдун консультациясы")
        for m in st.session_state.psy_chat:
            with st.chat_message(m["role"]): st.write(m["content"])
        if p_in := st.chat_input("Суроо жазыңыз..."):
            st.session_state.psy_chat.append({"role": "user", "content": p_in})
            r = client.chat.completions.create(messages=[{"role":"system","content":"Сиз жылуу маанайдагы психологсуз."}] + st.session_state.psy_chat, model="llama-3.1-8b-instant")
            st.session_state.psy_chat.append({"role": "assistant", "content": r.choices[0].message.content})
            st.rerun()

st.markdown("---")
st.caption("© 2026 HALIMA AI v7.0")