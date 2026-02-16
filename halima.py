import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq
import PyPDF2
import datetime
import random
import io

# --- 1. ПЛАТФОРМА ЖӨНДӨӨЛӨРҮ ---
st.set_page_config(page_title="HALIMA AI v5.0", layout="wide", page_icon="🤖")

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
if 'my_files' not in st.session_state: st.session_state.my_files = {}

# --- 2. ГЕОГРАФИЯЛЫК БАЗА (КР РАЙОНДОРУ) ---
regions_data = {
    "Жалал-Абад": ["Ноокен", "Сузак", "Базар-Коргон", "Аксы", "Токтогул", "Ала-Бука"],
    "Ош": ["Кара-Суу", "Араван", "Өзгөн", "Ноокат", "Алай"],
    "Чүй": ["Аламүдүн", "Сокулук", "Жайыл", "Ысык-Ата", "Кемин"],
    "Баткен": ["Кадамжай", "Лейлек", "Баткен"],
    "Талас": ["Манас", "Бакай-Ата", "Кара-Буура", "Талас"],
    "Нарын": ["Кочкор", "Ат-Башы", "Жумгал", "Ак-Талаа"],
    "Ысык-Көл": ["Түп", "Жети-Өгүз", "Ак-Суу", "Тоң"]
}

# --- 3. АВТОРИЗАЦИЯ ---
if not st.session_state.auth:
    st.title("🔐 HALIMA AI - Эксперттик Платформага кирүү")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user = st.text_input("Колдонуучунун аты:")
        pwd = st.text_input("Пароль:", type="password")
        if st.button("Кирүү", use_container_width=True):
            if pwd == "2026":
                st.session_state.auth = True
                st.session_state.user_name = user
                st.rerun()
            else: st.error("Пароль туура эмес!")
    st.stop()

# --- 4. БАШКЫ ГЕЙТ ---
if st.session_state.app_mode == "gate":
    st.title(f"🚀 Кош келиңиз, {st.session_state.user_name}!")
    col_agro, col_edu = st.columns(2)
    with col_agro:
        st.info("🚜 **АГРОНОМИЯ**\n\nЭкономикалык эсептөөлөр, топурак анализи жана райондук эксперттик корутунду.")
        if st.button("Агрономияга өтүү", use_container_width=True):
            st.session_state.app_mode = "agro"; st.rerun()
    with col_edu:
        st.success("🎓 **БИЛИМ БЕРҮҮ**\n\nПедагогикалык методдор, профориентация жана профессионал психолог.")
        if st.button("Билим берүүгө өтүү", use_container_width=True):
            st.session_state.app_mode = "edu"; st.rerun()
    st.stop()

# --- SIDEBAR (БАШКАРУУ) ---
with st.sidebar:
    st.header(f"👤 @{st.session_state.user_name}")
    if st.button("🏠 Башкы меню"):
        st.session_state.app_mode = "gate"; st.rerun()
    st.markdown("---")
    st.write(f"📅 Дата: {datetime.datetime.now().strftime('%d.%m.%Y')}")

# =================================================================
# --- 5. АГРОНОМИЯ БӨЛҮМҮ (ЖАҢЫЛАНДЫ) ---
# =================================================================
if st.session_state.app_mode == "agro":
    st.header("🚜 Улуттук Агро-Экономикалык Экспертиза")
    
    agro_tabs = st.tabs(["📊 Аналитика", "🧪 Топурак Лабораториясы", "📅 Агро-Календарь"])

    with agro_tabs[0]:
        col_inp, col_res = st.columns([1, 2])
        
        with col_inp:
            st.subheader("📍 Локация жана Параметрлер")
            reg = st.selectbox("Облус:", list(regions_data.keys()))
            dist = st.selectbox("Район:", regions_data[reg])
            crop = st.text_input("Өсүмдүк:", "Күрүч")
            
            st.markdown("---")
            st.subheader("💰 Экономика")
            area = st.number_input("Жер көлөмү (сотик):", value=10)
            seed_p = st.number_input("Үрөн/Көчөт баасы (сом/сотик):", value=300)
            
            if st.button("🚀 Профессионалдык Анализ", use_container_width=True):
                with st.spinner("Агро-ИИ эксперттик корутунду даярдоодо..."):
                    p = f"""Сиз КРнын жогорку категориядагы агрономусуз. 
                    Район: {dist}, Өсүмдүк: {crop}, Жер: {area} сотик.
                    Сураныч, төмөнкүлөрдү камтыган профессионалдык план бериңиз:
                    1. Агро-техникалык карта (айдоодон баштап жыйноого чейинки этаптар).
                    2. Сугаруу режими: {dist} районунун климатына ылайык канча жолу жана канча м3?
                    3. Экономикалык прогноз: 1 сотикке кеткен чыгым жана таза пайда (сом менен).
                    4. Райондук өзгөчөлүк: Бул райондо бул өсүмдүктүн илдеттери (зыянкечтери) жана алдын алуу.
                    Жоопту профессионалдык тилде, таблицалар менен бер."""
                    
                    res = client.chat.completions.create(messages=[{"role":"user","content":p}], model="llama-3.3-70b-versatile")
                    st.session_state.agro_out = res.choices[0].message.content

        with col_res:
            st.subheader(f"🌦 {dist} району: Аба ырайы жана Нымдуулук")
            weather_df = pd.DataFrame({
                "Күн": ["Бүгүн", "Эртең", "3-күн", "4-күн", "5-күн"],
                "Темп (°C)": [random.randint(15, 30) for _ in range(5)],
                "Нымдуулук (%)": [random.randint(20, 80) for _ in range(5)]
            })
            fig = px.bar(weather_df, x="Күн", y="Темп (°C)", color="Нымдуулук (%)", title="Температура жана топурактагы нымдуулук болжолу")
            st.plotly_chart(fig, use_container_width=True)
            
            if 'agro_out' in st.session_state:
                st.markdown(st.session_state.agro_out)
                st.download_button("📥 Толук Эксперттик Отчетту жүктөө", st.session_state.agro_out, f"agro_report_{dist}.txt")

    with agro_tabs[1]:
        st.subheader("🧪 Топурактын химиялык анализи (Виртуалдык)")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            ph = st.slider("Топурактын pH деңгээли:", 4.0, 9.0, 7.0)
            nitrogen = st.slider("Азот (N) мг/кг:", 0, 300, 150)
            phosphor = st.slider("Фосфор (P) мг/кг:", 0, 300, 150)
        with col_s2:
            kalii = st.slider("Калий (K) мг/кг:", 0, 400, 200)
            if st.button("Анализ жана Сунуш"):
                p = f"Топурак анализи: pH={ph}, N={nitrogen}, P={phosphor}, K={kalii}. {crop} үчүн кандай жер семирткичтер керек жана нормасы кандай?"
                res = client.chat.completions.create(messages=[{"role":"user","content":p}], model="llama-3.3-70b-versatile")
                st.info(res.choices[0].message.content)

    with agro_tabs[2]:
        st.subheader("📅 Сезондук иштердин календары")
        months = ["Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь"]
        selected_month = st.select_slider("Айды тандаңыз:", options=months)
        st.write(f"📌 **{selected_month}** айында {dist} районунда {crop} үчүн маанилүү иштер:")
        if st.button("Календарды алуу"):
             p = f"Кыргызстан, {dist} району. {selected_month} айында {crop} өсүмдүгүнө кандай кам көрүү керек? Кыскача 5 пункт."
             res = client.chat.completions.create(messages=[{"role":"user","content":p}], model="llama-3.3-70b-versatile")
             st.success(res.choices[0].message.content)

# =================================================================
# --- 6. БИЛИМ БЕРҮҮ БӨЛҮМҮ ---
# =================================================================
elif st.session_state.app_mode == "edu":
    st.header("🎓 Санариптик Билим Берүү Борбору")
    tabs = st.tabs(["🛠 Методдор (Мугалим)", "🎯 Кесип Тандоо (Окуучу)", "🧠 Психолог", "🌐 Изилдөө"])

    # --- ТАБ 1: ПЕДАГОГИКАЛЫК МЕТОДДОР ---
    with tabs[0]:
        st.subheader("🛠 Сабактын конструктору (Методдор)")
        col_m, col_p = st.columns([1, 2])
        with col_m:
            m_topic = st.text_input("Сабактын темасы:", "Фотосинтез")
            method = st.selectbox("Педагогикалык метод:", ["Сократ (Суроо-жооп)", "Коменский (Система)", "Сухомлинский (Жүрөк берүү)", "Макаренко (Коллектив)"])
            if st.button("План түзүү"):
                p = f"Сиз профессионал педагогсуз. {m_topic} темасын {method} методу менен өтүү үчүн толук сабактын планын түзүп бериңиз. Экспортко ылайыктуу таблица түрүндө бер."
                res = client.chat.completions.create(messages=[{"role":"user","content":p}], model="llama-3.3-70b-versatile")
                st.session_state.lesson_plan = res.choices[0].message.content
        with col_p:
            if 'lesson_plan' in st.session_state:
                st.markdown(st.session_state.lesson_plan)
                st.download_button("📥 Планды жүктөө", st.session_state.lesson_plan, "lesson_plan.txt")

    # --- ТАБ 2: ПРОФОРИЕНТАЦИЯ ---
    with tabs[1]:
        st.subheader("🎯 Кесиптик багыт берүү анализи")
        with st.form("pro_form"):
            st.write("Суроолорго жооп бериңиз (0-10):")
            s1 = st.slider("Техника жана приборлор менен иштөө:", 0, 10, 5)
            s2 = st.slider("Адамдар менен баарлашуу жана окутуу:", 0, 10, 5)
            s3 = st.slider("Чыгармачылык жана искусство:", 0, 10, 5)
            s4 = st.slider("Математика жана маалыматтар:", 0, 10, 5)
            sub_pro = st.form_submit_button("Анализ кылуу")
        
        if sub_pro:
            now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
            scores = {"Техникалык": s1, "Социалдык": s2, "Чыгармачылык": s3, "Аналитикалык": s4}
            fig = go.Figure(data=go.Scatterpolar(r=list(scores.values()), theta=list(scores.keys()), fill='toself'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])))
            st.plotly_chart(fig)
            
            p = f"Окуучунун упайлары: {scores}. Ага Кыргызстандагы кесиптерди жана университеттерди сунушта."
            res = client.chat.completions.create(messages=[{"role":"user","content":p}], model="llama-3.3-70b-versatile")
            ans = res.choices[0].message.content
            st.write(ans)
            st.session_state.pro_history.append({"дата": now, "жыйынтык": ans})

    # --- ТАБ 3: ПРОФЕССИОНАЛ ПСИХОЛОГ ---
    with tabs[2]:
        st.subheader("🧠 Психолог-Педагогдун консультациясы")
        for m in st.session_state.psy_chat:
            with st.chat_message(m["role"]): st.write(m["content"])
        
        if psy_in := st.chat_input("Сурооңузду жазыңыз..."):
            st.session_state.psy_chat.append({"role": "user", "content": psy_in})
            with st.chat_message("user"): st.write(psy_in)
            
            p = "Сиз 20 жылдык тажрыйбасы бар профессионал психолог-педагогсуз. Колдонуучуга жылуу жана илимий негизделген кеңеш бериңиз."
            r = client.chat.completions.create(messages=[{"role":"system","content":p}] + st.session_state.psy_chat, model="llama-3.3-70b-versatile")
            resp = r.choices[0].message.content
            st.session_state.psy_chat.append({"role": "assistant", "content": resp})
            with st.chat_message("assistant"): st.write(resp)

    # --- ТАБ 4: ИЗИЛДӨӨ ЖАНА БУЛАКТАР ---
    with tabs[3]:
        st.subheader("🌐 Илимий Изилдөө (Булактар менен)")
        iq = st.text_input("Изилдөө темасы:")
        if st.button("Изилдөөнү башта"):
            p = f"Тема: {iq}. Бул боюнча дүйнөлүк деңгээлде толук маалымат бер жана колдонгон сайттарыңды (Wikipedia, UNESCO ж.б.) шилтеме катары тизмекте."
            res = client.chat.completions.create(messages=[{"role":"user","content":p}], model="llama-3.3-70b-versatile")
            st.markdown(res.choices[0].message.content)
            st.download_button("📥 Изилдөөнү жүктөө", res.choices[0].message.content, "research.txt")

# --- 7. ПРЕЗЕНТАЦИЯ ҮЧҮН ЭСКЕРТҮҮ (ROADMAP) ---
st.markdown("---")
with st.expander("🚀 HALIMA AI 2026: Келечектеги өнүгүү планы (Roadmap)"):
    st.write("""
    1. **Voice-to-Text:** Мугалимдер үчүн үндү сабактын конспектине айлантуу модулу.
    2. **Инклюзивдик билим:** Көрүүсү начар окуучулар үчүн аудио-сабактарды автоматтык түзүү.
    3. **Агро-Сүрөт:** Өсүмдүк ооруларын сүрөт аркылуу аныктоо (Computer Vision).
    """)