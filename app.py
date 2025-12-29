import streamlit as st
import google.generativeai as genai
import json

# إعداد الصفحة
st.set_page_config(page_title="المقدر الهندسي الذكي", page_icon="🏗️", layout="wide")

# محاولة جلب المفتاح
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = None

def get_ai_data(item, qty):
    # 1. التحقق من وجود المفتاح
    if not api_key:
        return {"error": "لم يتم العثور على مفتاح API. تأكد من إضافته في Secrets."}
    
    # 2. إعداد الاتصال بجوجل
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        أنت خبير تسعير هندسي. حلل بند: "{item}"، الكمية: {qty}.
        الرد يجب أن يكون JSON فقط بالصيغة التالية:
        {{
        "unit": "وحدة القياس",
        "rate": "معدل الانتاج اليومي (رقم فقط)",
        "days": "عدد الايام (رقم فقط)",
        "crew": "تفاصيل الطاقم",
        "equip": "المعدات",
        "notes": "ملاحظة فنية"
        }}
        """
        
        response = model.generate_content(prompt)
        
        # تنظيف النص من علامات الكود في حال ظهرت
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)

    except Exception as e:
        # هذا السطر سيكشف لنا سبب المشكلة الحقيقي
        return {"error": str(e)}

# --- واجهة التطبيق ---
st.title("🏗️ المرجع الهندسي (AI Powered)")

col1, col2 = st.columns([3, 1])
with col1:
    item_name = st.text_input("اسم البند (مثال: حفر، سيراميك)")
with col2:
    quantity = st.number_input("الكمية", value=100.0)

if st.button("احسب الآن 🚀"):
    if not item_name:
        st.warning("اكتب اسم البند أولاً")
    else:
        with st.spinner("جاري التحليل..."):
            data = get_ai_data(item_name, quantity)
            
            # التحقق من وجود أخطاء
            if "error" in data:
                st.error(f"❌ حدث خطأ تقني:\n\n{data['error']}")
            else:
                # عرض النتائج في حال النجاح
                m1, m2, m3 = st.columns(3)
                m1.metric("الوحدة", data.get('unit', '-'))
                m2.metric("الانتاجية", data.get('rate', '-'))
                m3.metric("المدة", f"{data.get('days', '-')} يوم")
                
                st.success(f"**العمالة:** {data.get('crew', '-')}")
                st.info(f"**المعدات:** {data.get('equip', '-')}")
                st.warning(f"**ملاحظة:** {data.get('notes', '-')}")
