import streamlit as st
import google.generativeai as genai
import pypdf
import io

st.set_page_config(
    page_title="StudyFlow - المساعد الدراسي الذكي",
    page_icon="🎓",
    layout="wide"
)

api_key = st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("⚠️ لم يتم العثور على مفتاح GEMINI_API_KEY في إعدادات الأسرار (Secrets). يرجى إضافته لتشغيل الذكاء الاصطناعي.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

def extract_text(uploaded_file):
    try:
        if uploaded_file.name.endswith('.txt'):
            return uploaded_file.getvalue().decode('utf-8')
        elif uploaded_file.name.endswith('.pdf'):
            pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
        return None

st.title("🎓 StudyFlow - المساعد الدراسي الذكي")
st.write("ارفع ملف المحاضرة (PDF/TXT) واحصل على ملخص شامل واختبار مراجعة سريعة!")

uploaded_file = st.file_uploader("اختر ملف المستندات", type=["pdf", "txt"])

if uploaded_file and api_key:
    with st.spinner("جاري قراءة المستند..."):
        text_content = extract_text(uploaded_file)
    
    if text_content:
        st.success("تم تحليل المستند بنجاح!")
        tab1, tab2, tab3 = st.tabs(["📌 الملخص الشامل", "📝 اختبار المراجعة", "📄 النص الأصلي"])
        
        with tab1:
            if st.button("توليد الملخص 🚀"):
                with st.spinner("جاري التلخيص بواسطة Gemini..."):
                    prompt = f"قم بتلخيص النص التالي بأسلوب منظم ونقاط رئيسية باللغة العربية:\n\n{text_content[:15000]}"
                    res = model.generate_content(prompt)
                    st.markdown("### 📝 الملخص:")
                    st.write(res.text)
                    
        with tab2:
            if st.button("توليد أسئلة الاختبار 🧠"):
                with st.spinner("جاري إعداد الأسئلة..."):
                    prompt = f"بناءً على النص، أنشئ 5 أسئلة اختيار من متعدد مع الحل والتوضيح باللغة العربية:\n\n{text_content[:15000]}"
                    res = model.generate_content(prompt)
                    st.markdown("### ❓ الأسئلة:")
                    res_text = res.text if hasattr(res, 'text') else ""
                    st.write(res_text)
                    
        with tab3:
            st.text_area("محتوى الملف", text_content, height=300)
