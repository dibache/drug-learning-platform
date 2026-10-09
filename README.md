```markdown
# 💊 سامانه آموزش و مدیریت اطلاعات دارویی (Drug Learning & Clinical Platform)

یک پلتفرم وب مدرن و پیشرفته برای دانشجویان داروسازی (ویژه کارآموزی عرصه ۱ - اطلاعات دارویی) که با فریم‌ورک قدرتمند **Django** و طراحی رابط کاربری **Dark Mode با افکت‌های Glassmorphism** توسعه داده شده است.

---

## ✨ ویژگی‌های کلیدی پروژه (Key Features)

- **🔐 احراز هویت اختصاصی:** سیستم ورود و ثبت‌نام امن بر اساس شماره دانشجویی و کد ملی.
- **📚 مرکز یادگیری بالینی:** دسترسی به مباحث ۱۲ گانه تخصصی کارآموزی همراه با سوالات و سناریوهای بالینی.
- **📦 جعبه لایتنر هوشمند:** قابلیت افزودن سریع داروهای داخل تست‌ها به لایتنر شخصی برای مرور فعال نکات بالینی.
- **🏆 لیگ و رنکینگ دانشجویان:** سیستم رقابتی بر اساس مجموع سکه‌های فارما (🪙) و امتیاز کاپ بالینی (🏆).
- **⚡ پنل مدیریت اختصاصی (Custom Admin):** داشبورد مدیریت کاملاً یکدست با ظاهر سایت (بدون نیاز به استفاده از پنل پیش‌فرض جنگو) برای مدیریت مباحث، افزودن سوالات تستی و اعطای سکه به دانشجویان.
- **📱 طراحی موبایل-فرست (Mobile-First):** دارای منوی شناور پایین (Bottom Navigation) شیشه‌ای برای دسترسی فوق‌العاده روان در موبایل و تبلت.

---

## 🛠 تکنولوژی‌های استفاده شده (Tech Stack)

- **Backend:** Python, Django 5.x
- **Frontend:** HTML5, CSS3, Modern Flexbox & Grid, Glassmorphism UI Design
- **Icons & UI Effects:** Bootstrap Icons, CSS Backdrop Filter Blur
- **Database:** SQLite (قابل ارتقا به PostgreSQL در محیط پروداکشن)

---

## 📂 ساختار پروژه (Project Structure)

```text
drug_project/
│
├── drug_app_core/               # اپلیکیشن اصلی سامانه
│   ├── migrations/              # فایل‌های مهاجرت دیتابیس
│   ├── templates/               # قالب‌های HTML (داشبورد، یادگیری، پروفایل، لایتنر، لیگ و ادمین)
│   ├── admin.py                 # تنظیمات ادمین جنگو
│   ├── models.py                # مدل‌های دیتابیس (کاربر، مبحث، سوال، لایتنر)
│   ├── urls.py                  # مسیردهی‌های اپلیکیشن
│   └── views.py                 # منطق و ویوهای جنگو
│
├── drug_project/                # تنظیمات اصلی پروژه جنگو
│   ├── settings.py              # تنظیمات کلی (دیتابیس، استاتیک‌ها، امنیت)
│   ├── urls.py                  # مسیردهی اصلی روت
│   └── wsgi.py / asgi.py        # تنظیمات سرور
│
├── manage.py                    # ابزار مدیریتی جنگو
└── requirements.txt             # کتابخانه‌های پایتون مورد نیاز

```

---

## 🚀 راهنمای نصب و راه‌اندازی محلی (Installation Guide)

اگر می‌خواهید این پروژه را روی سیستم خود اجرا کنید، مراحل زیر را دنبال کنید:

1. **کلون کردن مخزن:**
```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd drug_project

```


2. **ساخت و فعال‌سازی محیط مجازی (Virtual Environment):**
```bash
python -m venv drug_env
# در ویندوز:
drug_env\Scripts\activate
# در مک/لینوکس:
source drug_env/bin/activate

```


3. **نصب پکیج‌ها و وابستگی‌ها:**
```bash
pip install django

```


4. **اجرای مهاجرت‌های دیتابیس (Migrations):**
```bash
python manage.py makemigrations
python manage.py migrate

```


5. **اجرای سرور لوکال:**
```bash
python manage.py runserver

```


اکنون می‌توانید در مرورگر به آدرس `http://127.0.0.1:8000/` مراجعه کنید.

---
