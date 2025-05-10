# 📨 پیام‌رسان Django با احراز هویت OTP و Celery

پروژه‌ای مبتنی بر Django REST Framework برای مدیریت کاربران با قابلیت:

- احراز هویت با OTP
- لیست کاربران با جست‌وجو، مرتب‌سازی، و صفحه‌بندی
- مستندسازی کامل API با Swagger
- اجرای تسک‌های غیربلوک با Celery + Redis
- اجرای کامل با Docker Compose

---

## 🏗 ساختار پروژه

```
.
├── accounts/           # اپ مدیریت کاربران و OTP
├── messenger/          # اپ اصلی پروژه
├── requirements.txt    # لیست پکیج‌های مورد نیاز
├── docker-compose.yml  # اجرای تمام سرویس‌ها
├── Dockerfile          # برای اجرای Django
├── celery.py           # تنظیمات Celery
└── README.md           # این فایل
```

---

## 🚀 نحوه اجرا (Docker)

### پیش‌نیازها:

- Docker
- Docker Compose

### اجرای پروژه:

```bash
git clone https://github.com/your-org/your-repo.git
cd your-repo

# ساخت و اجرای همه سرویس‌ها (وب، Celery، Redis)
docker-compose up --build
```

---

## 🧩 سرویس‌های Docker

| سرویس   | توضیح                           | پورت |
| ------- | ------------------------------- | ---- |
| web     | اپ Django                       | 8000 |
| celery  | تسک‌گیر برای تسک‌های async      | -    |
| redis   | بروکر پیام برای Celery          | 6379 |
| swagger | مستندات API در مسیر `/swagger/` | 8000 |

---

## 🔐 احراز هویت OTP

### مسیرهای مهم:

| متد  | URL                   | توضیح                    |
| ---- | --------------------- | ------------------------ |
| POST | `/accounts/register/` | دریافت کد OTP برای شماره |
| POST | `/accounts/verify/`   | تأیید OTP و دریافت توکن  |
| GET  | `/accounts/profile/`  | پروفایل کاربر لاگین شده  |

---

## 👥 لیست کاربران

### مسیر:

```
GET /accounts/users/
```

### پارامترهای پشتیبانی‌شده:

| پارامتر     | نوع    | توضیح                        |
| ----------- | ------ | ---------------------------- |
| `search`    | string | جست‌وجو بر اساس نام یا شماره |
| `ordering`  | string | مرتب‌سازی (مثلاً `username`) |
| `page`      | int    | شماره صفحه                   |
| `page_size` | int    | تعداد آیتم در هر صفحه        |

---

## 📚 مستندسازی API

مستندات Swagger در مسیر زیر:

```
http://localhost:8000/swagger/
```

---

## ⚙ تنظیمات مهم

### فایل `.env` (پیشنهادی)

```env
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_URL=redis://redis:6379/0
```

---

## 🐇 Celery

### فایل راه‌اندازی:

`messenger/celery.py`

### اجرای خودکار در Docker:

```yaml
services:
  celery:
    build: .
    command: celery -A messenger worker -l info
```

---

## ✅ تست دستی OTP (با curl)

```bash
curl -X POST http://localhost:8000/accounts/register/      -H "Content-Type: application/json"      -d '{"phone_number": "09121234567"}'
```

---

## ⚠ نکات توسعه

- اگر تغییری در dependency داشتید، دستور زیر را فراموش نکنید:

```bash
docker-compose build --no-cache
```

- برای ورود به محیط Bash کانتینر:

```bash
docker exec -it your_project_web_1 bash
```

---

## 🧪 تست‌ها (در حال توسعه)

> تست‌های مربوط به OTP و API لیست کاربران به زودی افزوده خواهند شد.

---

## 📌 TODO

- [x] احراز هویت OTP
- [x] Celery + Redis
- [x] مستندات Swagger
- [ ] ارسال پیام بین کاربران
- [ ] لاگ فعالیت کاربران
- [ ] تست‌های پوشش‌دهی کامل

---

## 👤 توسعه‌دهنده

- نویسنده: ‌behnam bashiri
- ایمیل: behnambashiri80@gmail.com

---
