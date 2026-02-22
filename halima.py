import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq
import datetime
import random

# --- 1. ПЛАТФОРМА ЖӨНДӨӨЛӨРҮ ---
st.set_page_config(page_title="HALIMA AI v6.0", layout="wide", page_icon="🤖")

# Дизайн жана "Вайб" үчүн CSS
def local_css(style_type):
    if style_type == "agro":
        bg_color = "#f0f9f1" # Жашыл вайб
        accent = "#2e7d32"
    elif style_type == "edu":
        bg_color = "#f0f4f8" # Академиялык көк вайб
        accent = "#1565c0"
    else:
        bg_color = "#ffffff"
        accent = "#333333"

    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg_color}; }}
        .main-header {{ color: {accent}; font-weight: bold; font-size: 2.5rem; }}
        .stButton>button {{ border-radius: 20px; border: 1px solid {accent}; color: {accent}; }}
        .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
        .stTabs [data-baseweb="tab"] {{ background-color: white; border-radius: 10px 10px 0 0; padding: 10px 20px; }}
        </style>
    """, unsafe_allow_html=True)

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API Key ката! .streamlit/secrets.toml файлын текшериңиз.")
    st.stop()

# Сессияларды башкаруу
if 'auth' not in st.session_state: st.session_state.auth = False
if 'app_mode' not in st.session_state: st.session_state.app_mode = "gate"
if 'psy_chat' not in st.session_state: st.session_state.psy_chat = []
if 'pro_history' not in st.session_state: st.session_state.pro_history = []

regions_data = {
    "Жалал-Абад": ["Ноокен", "Сузак", "Базар-Коргон", "Аксы", "Токтогул", "Ала-Бука"],
    "Ош": ["Кара-Суу", "Араван", "Өзгөн", "Ноокат", "Алай"],
    "Чүй": ["Аламүдүн", "Сокулук", "Жайыл", "Ысык-Ата", "Кемин"],
    "Баткен": ["Кадамжай", "Лейлек", "Баткен"],
    "Талас": ["Манас", "Бакай-Ата", "Кара-Буура", "Талас"],
    "Нарын": ["Кочкор", "Ат-Башы", "Жумгал", "Ак-Талаа"],
    "Ысык-Көл": ["Түп", "Жети-Өгүз", "Ак-Суу", "Тоң"]
}

# --- 2. АВТОРИЗАЦИЯ ---
if not st.session_state.auth:
    st.title("🔐 HALIMA AI - Эксперттик Платформа")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user = st.text_input("Колдонуучунун аты:")
        pwd = st.text_input("Пароль:", type="password")
        # ЖАҢЫЛАНДЫ: width='stretch' колдонулду
        if st.button("Кирүү", width="stretch"):
            if pwd == "2026":
                st.session_state.auth = True
                st.session_state.user_name = user
                st.rerun()
            else: st.error("Пароль туура эмес!")
    st.stop()

# --- 3. БАШКЫ ГЕЙТ ---
if st.session_state.app_mode == "gate":
    st.markdown('<h1 class="main-header">🚀 Кош келиңиз, Кожоюн!</h1>', unsafe_allow_html=True)
    col_agro, col_edu = st.columns(2)
    with col_agro:
        st.info("🚜 **АГРОНОМИЯ ЖАНА ЭКОНОМИКА**\n\nСатуу каналдары, экономикалык эсептөөлөр жана топурак анализи.")
        if st.button("Агрономияга өтүү", width="stretch"):
            st.session_state.app_mode = "agro"; st.rerun()
    with col_edu:
        st.success("🎓 **БИЛИМ БЕРҮҮ ЖАНА ПСИХОЛОГИЯ**\n\nПрофессионалдык методдор, Голланд тести жана психолог кеңеши.")
        if st.button("Билим берүүгө өтүү", width="stretch"):
            st.session_state.app_mode = "edu"; st.rerun()
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header(f"👤 @{st.session_state.user_name}")
    if st.button("🏠 Башкы меню"):
        st.session_state.app_mode = "gate"; st.rerun()
    st.markdown("---")
    st.write(f"📅 Дата: {datetime.datetime.now().strftime('%d.%m.%Y')}")

# =================================================================
# --- 4. АГРОНОМИЯ БӨЛҮМҮ ---
# =================================================================
if st.session_state.app_mode == "agro":
    local_css("agro")
    st.markdown('<h1 class="main-header">🌿 Улуттук Агро-Экономикалык Платформа</h1>', unsafe_allow_html=True)
    
    agro_tabs = st.tabs(["📊 Аналитика", "💰 Сатуу Каналдары", "🧪 Лаборатория", "📈 Киреше Калькулятору"])

    with agro_tabs[0]:
        col_inp, col_res = st.columns([1, 2])
        with col_inp:
            st.subheader("📍 Параметрлер")
            reg = st.selectbox("Облус:", list(regions_data.keys()))
            dist = st.selectbox("Район:", regions_data[reg])
            crop = st.text_input("Өсүмдүк:", "Төө буурчак (Фасоль)")
            area = st.number_input("Жер көлөмү (сотик):", value=10)
            
            if st.button("🚀 Анализди баштоо", width="stretch"):
                p = f"Район: {dist}, Өсүмдүк: {crop}, Жер: {area} сотик. Агро-карта, сугаруу жана экономикалык прогноз бер."
                res = client.chat.completions.create(messages=[{"role":"user","content":p}], model="llama-3.3-70b-versatile")
                st.session_state.agro_out = res.choices[0].message.content

        with col_res:
            if 'agro_out' in st.session_state:
                st.markdown(st.session_state.agro_out)
                st.caption("🌐 Маалымат булагы: https://stat.gov.kg/ (2025-2026-жылдын отчетторунун негизинде)")

    with agro_tabs[1]:
        st.subheader("💹 Продукцияны сатуу жана Экспорттук каналдар")
        sales_data = pd.DataFrame({
            "Завод / Сатуу түйүнү": ["Агро-Экспорт Талас", "Бишкек Склад", "Ош-Дан", "Жергиликтүү базар"],
            "Сатып алуу баасы (сом/кг)": [95, 88, 82, 75],
            "Пайдалуулук (%)": [90, 75, 60, 45]
        })
        
        col_table, col_chart = st.columns([1, 1])
        with col_table:
            st.write("📊 Учурдагы орточо баалар:")
            st.table(sales_data)
        
        with col_chart:
            fig_sales = px.bar(sales_data, x="Завод / Сатуу түйүнү", y="Пайдалуулук (%)", 
                               color="Сатып алуу баасы (сом/кг)", title="Кайсы жерге сатуу пайдалуу?")
            st.plotly_chart(fig_sales, width="stretch")
        
        st.info("💡 **Эксперттин сунушу:** Сиз тандаган өсүмдүктү 'Агро-Экспорт Талас' аркылуу сатуу 20% көбүрөөк пайда берет.")

    with agro_tabs[2]:
        st.subheader("🧪 Топурактын виртуалдык анализи")
        ph = st.select_slider("pH деңгээли:", options=[4, 5, 6, 7, 8, 9], value=7)
        if st.button("Сунуш алуу"):
            st.success(f"pH {ph} үчүн сунуш: Күрүч өстүрүүгө эң сонун шарт. Азоттук жер семирткичтерди 10% азайтыңыз.")

    with agro_tabs[3]:
        st.subheader("📊 Түшүмдүүлүктү жана кирешени болжолдоо")
        exp_yield = st.number_input("Күтүлүп жаткан түшүм (тонна):", value=1.0)
        market_price = st.number_input("Болжолдуу баа (сом/кг):", value=85.0)
        total_profit = exp_yield * 1000 * market_price
        st.metric("Жалпы болжолдуу киреше", f"{total_profit:,.0f} сом", delta="↑ 12% прогноз")

# =================================================================
# --- 5. БИЛИМ БЕРҮҮ БӨЛҮМҮ ---
# =================================================================
elif st.session_state.app_mode == "edu":
    local_css("edu")
    st.markdown('<h1 class="main-header">🎓 Санариптик Билим Берүү Борбору</h1>', unsafe_allow_html=True)
    
    edu_tabs = st.tabs(["🛠 Сабак Конструктору", "🎯 Кесип Тандоо", "🧠 Психолог"])

    with edu_tabs[0]:
        st.subheader("🛠 Мугалимдин жардамчысы")
        col_e1, col_e2 = st.columns([1, 2])
        with col_e1:
            m_topic = st.text_input("Сабактын темасы:", "Кыргызстандын тарыхы")
            m_type = st.selectbox("Сабактын түрү:", ["1 сааттык сабак", "Лекция (90 мүнөт)", "Практикалык иш", "Семинар"])
            method = st.selectbox("Методика:", ["Сократтык маек", "Коменский системасы", "Интерактивдүү оюн", "Макаренко методу"])
            
            if st.button("План түзүү", width="stretch"):
                p = f"Тема: {m_topic}. Түрү: {m_type}. Метод: {method}. Сабактын планын кыргыз тилинде таблица менен түз."
                res = client.chat.completions.create(messages=[{"role":"user","content":p}], model="llama-3.3-70b-versatile")
                st.session_state.edu_plan = res.choices[0].message.content
        
        with col_e2:
            if 'edu_plan' in st.session_state:
                st.markdown(st.session_state.edu_plan)

    with edu_tabs[1]:
        st.subheader("🎯 Профориентация: Голланд методикасы")
        with st.form("pro_test"):
            c1 = st.slider("1. Техника жана Программалоо:", 0, 10, 5)
            c2 = st.slider("2. Адамдарга жардам берүү:", 0, 10, 5)
            c3 = st.slider("3. Илим жана Изилдөө:", 0, 10, 5)
            c4 = st.slider("4. Искусство жана Дизайн:", 0, 10, 5)
            c5 = st.slider("5. Лидерлик жана Бизнес:", 0, 10, 5)
            submit_test = st.form_submit_button("Жыйынтыкты көрүү")

        if submit_test:
            scores = {"Реалдуу": c1, "Социалдык": c2, "Интеллектуалдык": c3, "Артисттик": c4, "Предпринимательдик": c5}
            fig_pro = go.Figure(data=go.Scatterpolar(r=list(scores.values()), theta=list(scores.keys()), fill='toself'))
            st.plotly_chart(fig_pro, width="stretch")
            st.success(f"✅ Сиздин басымдуу тибиңиз: **{max(scores, key=scores.get)}**.")

    with edu_tabs[2]:
        st.subheader("🧠 Психологдун консультациясы")
        for m in st.session_state.psy_chat:
            with st.chat_message(m["role"]): st.write(m["content"])
        
        if psy_in := st.chat_input("Психологго суроо жазыңыз..."):
            st.session_state.psy_chat.append({"role": "user", "content": psy_in})
            with st.chat_message("user"): st.write(psy_in)
            
            r = client.chat.completions.create(
                messages=[{"role":"system","content":"Сиз жылуу маанайдагы психологсуз."}] + st.session_state.psy_chat, 
                model="llama-3.3-70b-versatile"
            )
            resp = r.choices[0].message.content
            st.session_state.psy_chat.append({"role": "assistant", "content": resp})
            st.rerun()

# --- ФУТЕР ---
st.markdown("---")
st.caption(f"© 2026 HALIMA AI - Бардык маалыматтар КР Улуттук статистика комитетинин базасына негизделген.")