import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq
import datetime
import docx
import PyPDF2
import base64

# --- 1. SETTINGS & STYLES (Сизге жаккан биринчи дизайн) ---
st.set_page_config(page_title="HALIMA AI v7.0", layout="wide", page_icon="🚀")

def local_css(style_type):
    primary_color = "#2E7D32" if style_type == "agro" else "#007AFF"
    gradient = "linear-gradient(135deg, #e8f5e9 0%, #ffffff 100%)" if style_type == "agro" else "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;600&display=swap');
        * {{ font-family: 'SF Pro Display', sans-serif; }}
        .stApp {{ background: {gradient}; }}
        div[data-testid="stExpander"], div.stButton > button, .stTabs {{
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 15px !important;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        }}
        .stButton > button {{
            transition: all 0.3s ease;
            border: none !important;
            background: {primary_color} !important;
            color: white !important;
            font-weight: 600;
            padding: 0.6rem 1rem;
        }}
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .main-header {{
            background: linear-gradient(to right, {primary_color}, #4facfe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 2rem;
        }}
        [data-testid="stSidebar"] {{
            background: rgba(255, 255, 255, 0.5);
            backdrop-filter: blur(10px);
        }}
        </style>
    """, unsafe_allow_html=True)

# --- 2. HELPERS ---
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
        return "Error reading file."

# --- 3. API & STATE ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("API Key error! Check .streamlit/secrets.toml")
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

# --- 4. LOGIN PAGE ---
if not st.session_state.auth:
    local_css("edu")
    st.markdown('<h1 class="main-header">HALIMA AI</h1>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div style='text-align: center;'><h3>Кош келиңиз! 👋</h3></div>", unsafe_allow_html=True)
        user = st.text_input("Колдонуучу:")
        pwd = st.text_input("Пароль:", type="password")
        if st.button("Кирүү 🔓", use_container_width=True):
            if pwd == "31012008":
                st.session_state.auth = True
                st.session_state.user_name = user
                st.rerun()
            else:
                st.error("Пароль туура эмес!")
    st.stop()

# --- 5. MAIN GATEWAY ---
if st.session_state.app_mode == "gate":
    local_css("edu")
    st.markdown('<h1 class="main-header">Багытты тандаңыз</h1>', unsafe_allow_html=True)
    col_agro, col_edu = st.columns(2, gap="large")
    with col_agro:
        st.markdown("<div style='text-align: center;'><h1 style='font-size: 80px;'>🌿</h1><h2>Агро-Экономика</h2></div>", unsafe_allow_html=True)
        if st.button("Агро дүйнөсүнө өтүү", use_container_width=True):
            st.session_state.app_mode = "agro"; st.rerun()
    with col_edu:
        st.markdown("<div style='text-align: center;'><h1 style='font-size: 80px;'>🎓</h1><h2>Билим берүү</h2></div>", unsafe_allow_html=True)
        if st.button("Билим борборуна өтүү", use_container_width=True):
            st.session_state.app_mode = "edu"; st.rerun()
    st.stop()

# --- 6. APP CONTENT ---
local_css(st.session_state.app_mode)
with st.sidebar:
    st.markdown(f"### 👤 @{st.session_state.user_name}")
    if st.button("🏠 Башкы меню", use_container_width=True):
        st.session_state.app_mode = "gate"; st.rerun()
    st.write(f"📅 {datetime.datetime.now().strftime('%d.%m.%Y')}")

# --- AGRO MODULE (Экинчи коддогу функциялар менен) ---
if st.session_state.app_mode == "agro":
    st.markdown('<h1 class="main-header">🌿 Агро-Экономикалык Платформа</h1>', unsafe_allow_html=True)
    
    # Сүрөт жана файл талдоо (Vision функциясы менен)
    with st.expander("🖼️ Сүрөт жана Документ Талдоо"):
        up_file = st.file_uploader("Файлды же сүрөттү жүктөңүз", type=['pdf', 'docx', 'jpg', 'png', 'jpeg'])
        if up_file:
            col_img, col_txt = st.columns([1, 2])
            if up_file.type.startswith('image'):
                with col_img: st.image(up_file, use_container_width=True)
            user_task = st.text_area("AI үчүн тапшырма:", placeholder="Текстти талда же сүрөттү чечмеле...")
            if st.button("✨ Талдоону баштоо"):
                with st.spinner("AI талдап жатат..."):
                    if up_file.type.startswith('image'):
                        base64_image = encode_image(up_file)
                        res = client.chat.completions.create(
                            messages=[{"role": "user", "content": [{"type": "text", "text": user_task or "Бул эмне?"}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}],
                            model="llama-3.2-11b-vision-instant"
                        )
                    else:
                        text = extract_text_from_file(up_file)
                        res = client.chat.completions.create(messages=[{"role":"user","content": f"{user_task}: {text[:2000]}"}], model="llama-3.1-8b-instant")
                    st.success(res.choices[0].message.content)

    tabs = st.tabs(["📊 Аналитика", "💰 Сатуу Каналдары", "🧮 Калькулятор"])
    
    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1: reg = st.selectbox("Облус:", list(regions_data.keys()))
        with c2: dist = st.selectbox("Район:", regions_data[reg])
        crop_input = st.text_input("Өсүмдүк түрү:", "Буудай")
        if st.button("🚀 Аналитикалык отчет алуу"):
            res = client.chat.completions.create(messages=[{"role":"user","content":f"Кыргызстандын {dist} районунда {crop_input} өстүрүү боюнча толук технологиялык карта жана кеңеш бер."}], model="llama-3.1-8b-instant")
            st.info(res.choices[0].message.content)

    with tabs[1]:
        st.subheader("📦 Сатуу жана Экспорт")
        market_type = st.selectbox("Базар түрү:", ["Жергиликтүү базар", "Экспорт (Россия/Казакстан)", "Органикалык базар"])
        if st.button("Сатуу жолдорун көрүү"):
            res = client.chat.completions.create(messages=[{"role":"user","content":f"Кыргызстанда {crop_input} өсүмдүгүн {market_type} аркылуу сатуунун жолдору."}], model="llama-3.1-8b-instant")
            st.write(res.choices[0].message.content)

    with tabs[2]:
        st.subheader("🧮 Түшүмдүүлүк Калькулятору")
        col1, col2 = st.columns(2)
        with col1:
            area_val = st.number_input("Аянт (гектар):", 1.0)
            seeds_val = st.number_input("Үрөн баасы (сом/кг):", 50)
        with col2:
            price_val = st.number_input("Сатуу баасы (сом/кг):", 80)
            yield_val = st.number_input("Күтүлгөн түшүм (кг/гектар):", 2000)
        if st.button("Эсептөө"):
            total_income = (yield_val * area_val * price_val) - (seeds_val * 200)
            st.metric("Болжолдуу таза киреше:", f"{total_income} сом")

# --- EDUCATION MODULE (Туураланган Сабак Конструктору менен) ---
elif st.session_state.app_mode == "edu":
    st.markdown('<h1 class="main-header">🎓 Санариптик Билим Борбору</h1>', unsafe_allow_html=True)
    
    tabs = st.tabs(["🛠 Сабак Конструктору", "🎯 Кесип Тандоо", "🧠 Психолог", "📄 Файл Анализ"])
    
    with tabs[0]:
        st.subheader("📚 Жаңы сабактын планы")
        subject = st.text_input("Предметтин аты:")
        topic = st.text_input("Сабактын темасы:")
        grade = st.slider("Класс:", 1, 11, 7)
        if st.button("План түзүү"):
            with st.spinner("План түзүлүп жатат..."):
                prompt = f"{grade}-класс үчүн {subject} предметинен '{topic}' темасына 45 мүнөттүк заманбап сабак планы (максаты, усулдары, тапшырмалары менен) кыргыз тилинде түзүп бер."
                res = client.chat.completions.create(messages=[{"role":"user","content": prompt}], model="llama-3.1-8b-instant")
                st.write(res.choices[0].message.content)

    with tabs[1]:
        st.subheader("🎯 Профориентация (Holland Test)")
        c1 = st.slider("Техникалык (R):", 0, 10, 5)
        c2 = st.slider("Илимий (I):", 0, 10, 5)
        c3 = st.slider("Чыгармачыл (A):", 0, 10, 5)
        c4 = st.slider("Социалдык (S):", 0, 10, 5)
        if st.button("Жыйынтыкты эсептөө"):
            scores = {"Реалдуу": c1, "Илим": c2, "Арт": c3, "Социал": c4}
            fig = go.Figure(data=go.Scatterpolar(r=list(scores.values()), theta=list(scores.keys()), fill='toself'))
            st.plotly_chart(fig)
            top = max(scores, key=scores.get)
            res = client.chat.completions.create(messages=[{"role":"user","content": f"Кыргызстанда {top} тибине ылайыктуу кесиптер."}], model="llama-3.1-8b-instant")
            st.write(res.choices[0].message.content)

    with tabs[2]:
        st.subheader("🧠 Психолог")
        for m in st.session_state.psy_chat:
            with st.chat_message(m["role"]): st.write(m["content"])
        if p_in := st.chat_input("Сүйлөшөлү..."):
            st.session_state.psy_chat.append({"role": "user", "content": p_in})
            r = client.chat.completions.create(messages=[{"role":"system","content":"Сиз психологсуз."}] + st.session_state.psy_chat, model="llama-3.1-8b-instant")
            st.session_state.psy_chat.append({"role": "assistant", "content": r.choices[0].message.content})
            st.rerun()

    with tabs[3]:
        edu_file = st.file_uploader("Документ жүктөңүз", type=['pdf', 'docx', 'txt'])
        if edu_file:
            task = st.text_input("Тапшырма (мис: Тест түз):")
            if st.button("🔍 Анализ"):
                text = extract_text_from_file(edu_file)
                res = client.chat.completions.create(messages=[{"role":"user","content": f"{task}\n\n{text[:2000]}"}], model="llama-3.1-8b-instant")
                st.write(res.choices[0].message.content)

st.markdown("<br><hr><center>© 2026 HALIMA AI | Designed for Innovation</center>", unsafe_allow_html=True)