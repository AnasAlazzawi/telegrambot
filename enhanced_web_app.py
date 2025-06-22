import gradio as gr
from gradio_client import Client, handle_file
import os
from PIL import Image
import tempfile
import time

# تهيئة العميل
def initialize_client(model_choice):
    try:
        if model_choice == "النموذج الأول - Kolors":
            client = Client("krsatyam7/Virtual_Clothing_Try-On-new")
        else:  # النموذج الثاني
            client = Client("PawanratRung/virtual-try-on")
        return client
    except Exception as e:
        print(f"خطأ في تهيئة العميل: {e}")
        return None

# دالة تجربة الملابس الافتراضية
def virtual_tryon(person_image, garment_image, model_choice, garment_type):
    if person_image is None:
        return None, "❌ الرجاء رفع صورة الشخص"
    
    if garment_image is None:
        return None, "❌ الرجاء رفع صورة الملابس"
    
    try:
        # تهيئة العميل
        client = initialize_client(model_choice)
        if client is None:
            return None, "❌ خطأ في الاتصال بالخدمة"
        
        # حفظ الصور مؤقتاً
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as person_temp:
            person_image.save(person_temp.name)
            person_temp_path = person_temp.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as garment_temp:
            garment_image.save(garment_temp.name)
            garment_temp_path = garment_temp.name
        
        # إجراء تجربة الملابس حسب النموذج المختار
        if model_choice == "النموذج الأول - Kolors":
            result = client.predict(
                person_image=handle_file(person_temp_path),
                clothing_image=handle_file(garment_temp_path),
                api_name="/swap_clothing"
            )
        else:  # النموذج الثاني
            result = client.predict(
                person_path=handle_file(person_temp_path),
                garment_path=handle_file(garment_temp_path),
                garment_type=garment_type,
                api_name="/virtual_tryon"
            )
        
        # تنظيف الملفات المؤقتة
        try:
            os.unlink(person_temp_path)
            os.unlink(garment_temp_path)
        except:
            pass
        
        if result:
            return result, f"✅ تم إنشاء النتيجة بنجاح باستخدام {model_choice}!"
        else:
            return None, "❌ فشل في إنشاء النتيجة"
            
    except Exception as e:
        return None, f"❌ خطأ: {str(e)}"

# دالة لإظهار/إخفاء خيار نوع الملابس
def toggle_garment_type(model_choice):
    if model_choice == "النموذج الثاني - PawanratRung":
        return gr.update(visible=True)
    else:
        return gr.update(visible=False)

# دالة تحميل ملف العنوان
def load_title():
    title_path = os.path.join("assets", "title.md")
    if os.path.exists(title_path):
        with open(title_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return """
# 👕 جرب الملابس افتراضياً
### ارفع صورة الشخص وصورة الملابس لرؤية النتيجة!
"""

# تحديد مسارات الأمثلة
example_path = os.path.join(os.path.dirname(__file__), 'assets')
garm_list_path = []
human_list_path = []

# تحميل أمثلة الملابس
cloth_path = os.path.join(example_path, "cloth")
if os.path.exists(cloth_path):
    garm_list = [f for f in os.listdir(cloth_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    garm_list_path = [os.path.join(cloth_path, garm) for garm in garm_list]

# تحميل أمثلة الأشخاص
human_path = os.path.join(example_path, "human")
if os.path.exists(human_path):
    human_list = [f for f in os.listdir(human_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    human_list_path = [os.path.join(human_path, human) for human in human_list]

# CSS للتصميم
css = """
#col-left, #col-mid, #col-right {
    margin: 0 auto;
    max-width: 400px;
}
#col-showcase {
    margin: 0 auto;
    max-width: 1000px;
}
#run-button {
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
    color: white;
    font-size: 18px;
    font-weight: bold;
    border: none;
    border-radius: 10px;
    padding: 15px 30px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
}
#run-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}
.custom-title {
    text-align: center;
    color: #2c3e50;
    margin-bottom: 20px;
}
.step-header {
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    padding: 10px;
    border-radius: 10px;
    text-align: center;
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 10px;
}
.model-info {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 4px solid #007bff;
}
"""

# إنشاء واجهة Gradio
with gr.Blocks(css=css, title="Virtual Try-On", theme=gr.themes.Soft()) as demo:
    
    # العنوان الرئيسي
    gr.HTML(f"""
    <div class="custom-title">
        <h1>👕 تطبيق تجربة الملابس الافتراضية</h1>
        <p>ارفع صورة شخص وصورة ملابس لرؤية النتيجة المذهلة!</p>
        <div class="model-info">
            <strong>🤖 نموذجان متاحان:</strong><br>
            • <strong>النموذج الأول (Kolors):</strong> أسرع وأبسط<br>
            • <strong>النموذج الثاني (PawanratRung):</strong> يدعم أنواع ملابس متنوعة
        </div>
    </div>
    """)
    
    # الخطوات
    with gr.Row():
        with gr.Column(elem_id="col-left"):
            gr.HTML('<div class="step-header">الخطوة 1: ارفع صورة الشخص 👤</div>')
            
        with gr.Column(elem_id="col-mid"):
            gr.HTML('<div class="step-header">الخطوة 2: ارفع صورة الملابس 👕</div>')
            
        with gr.Column(elem_id="col-right"):
            gr.HTML('<div class="step-header">الخطوة 3: اختر النموذج واضغط "جرب الآن" 🚀</div>')
    
    # المحتوى الرئيسي
    with gr.Row():
        with gr.Column(elem_id="col-left"):
            person_image = gr.Image(
                label="صورة الشخص",
                sources=['upload'],
                type="pil",
                height=400
            )
            
            # أمثلة الأشخاص
            if human_list_path:
                gr.Examples(
                    inputs=person_image,
                    examples=human_list_path[:8],
                    examples_per_page=4,
                    label="أمثلة الأشخاص"
                )
        
        with gr.Column(elem_id="col-mid"):
            garment_image = gr.Image(
                label="صورة الملابس",
                sources=['upload'],
                type="pil",
                height=400
            )
            
            # أمثلة الملابس
            if garm_list_path:
                gr.Examples(
                    inputs=garment_image,
                    examples=garm_list_path[:8],
                    examples_per_page=4,
                    label="أمثلة الملابس"
                )
        
        with gr.Column(elem_id="col-right"):
            # اختيار النموذج
            model_choice = gr.Radio(
                choices=["النموذج الأول - Kolors", "النموذج الثاني - PawanratRung"],
                value="النموذج الأول - Kolors",
                label="🤖 اختر النموذج",
                info="النموذج الأول أسرع، النموذج الثاني يدعم أنواع ملابس مختلفة"
            )
            
            # نوع الملابس (للنموذج الثاني فقط)
            garment_type = gr.Radio(
                choices=["upper_body", "lower_body", "dresses"],
                value="upper_body",
                label="👔 نوع الملابس (للنموذج الثاني فقط)",
                info="upper_body: قمصان وبلوزات | lower_body: بناطيل | dresses: فساتين",
                visible=False
            )
            
            result_image = gr.Image(
                label="النتيجة",
                height=400,
                show_share_button=True
            )
            
            # زر التشغيل
            run_button = gr.Button(
                "🚀 جرب الآن!",
                elem_id="run-button",
                size="lg"
            )
            
            # رسالة الحالة
            status_message = gr.Textbox(
                label="الحالة",
                interactive=False,
                placeholder="ستظهر رسالة الحالة هنا..."
            )
    
    # ربط تغيير النموذج بإظهار/إخفاء نوع الملابس
    model_choice.change(
        fn=toggle_garment_type,
        inputs=[model_choice],
        outputs=[garment_type]
    )
    
    # ربط الدالة بالزر
    run_button.click(
        fn=virtual_tryon,
        inputs=[person_image, garment_image, model_choice, garment_type],
        outputs=[result_image, status_message],
        api_name="virtual_tryon"
    )
    
    # قسم الأمثلة
    if os.path.exists(os.path.join(example_path, "examples")):
        gr.HTML("""
        <div style="text-align: center; margin-top: 40px;">
            <h2>🎨 أمثلة على النتائج</h2>
            <p>شاهد بعض الأمثلة على نتائج تجربة الملابس الافتراضية</p>
        </div>
        """)
        
        examples_showcase = gr.Examples(
            examples=[
                [
                    os.path.join(example_path, "examples", "model1.png"),
                    os.path.join(example_path, "examples", "garment1.png")
                ],
                [
                    os.path.join(example_path, "examples", "model2.png"),
                    os.path.join(example_path, "examples", "garment2.png")
                ],
                [
                    os.path.join(example_path, "examples", "model3.png"),
                    os.path.join(example_path, "examples", "garment3.png")
                ],
            ],
            inputs=[person_image, garment_image],
            label="أمثلة متنوعة"
        )
    
    # تذييل
    gr.HTML("""
    <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
        <p><strong>💡 نصائح للحصول على أفضل النتائج:</strong></p>
        <ul style="text-align: right; display: inline-block;">
            <li>استخدم صور عالية الجودة وواضحة</li>
            <li>تأكد من أن الشخص يظهر كاملاً في الصورة</li>
            <li>اختر ملابس بخلفية بسيطة</li>
            <li>تجنب الصور الضبابية أو المظلمة</li>
            <li>النموذج الثاني يحتاج تحديد نوع الملابس للحصول على أفضل النتائج</li>
        </ul>
    </div>
    """)

# تشغيل التطبيق
if __name__ == "__main__":
    print("🚀 بدء تشغيل تطبيق تجربة الملابس الافتراضية مع نموذجين...")
    demo.launch(
        server_name="127.0.0.1",
        server_port=7862,  # منفذ مختلف
        share=False,
        show_error=True
    )
