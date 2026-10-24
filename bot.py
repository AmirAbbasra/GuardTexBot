import os
import time
import requests
import random

TOKEN = os.getenv("RUBIKA_TOKEN")

if not TOKEN:
    raise SystemExit("توکن ربات تنظیم نشده است.")

BASE = f"https://botapi.rubika.ir/v3/{TOKEN}"
session = requests.Session()

REPLIES = {
    "سلام": [
        "سلام رفیق 😎",
        "سلام، خوبی؟ 🌹",
        "سلام به جمع باصفا! 🛡️"
    ],
    "خوبی": [
        "خوبم، مرسی! تو خوبی؟ ❤️",
        "آره، عالی‌ام 😁",
        "ممنون که پرسیدی 🌹"
    ],
    "چطوری": [
        "خوبم، تو چطوری؟ 😎",
        "همه‌چی روبه‌راهه، تو چه خبر؟"
    ],
    "خداحافظ": [
        "فعلاً رفیق، مراقب خودت باش 👋",
        "بای بای، زود برگرد ❤️"
    ],
    "چالش": [
        "🔥 چالش: سه تا از علایقت رو بگو!",
        "😎 چالش: یک حقیقت جالب درباره خودت بگو!",
        "🎯 چالش: اسم سه تا فیلم یا بازی محبوبت رو بگو!"
    ],
    "کوییز": [
        "🧠 سؤال: بزرگ‌ترین سیاره منظومه شمسی کدام است؟\nالف) زمین\nب) مشتری\nج) مریخ\nجواب رو بفرست!"
    ],
    "حقیقت": [
        "🤔 سؤال حقیقت: بهترین خاطره‌ات از امسال چیه؟",
        "💬 سؤال حقیقت: چه چیزی بیشتر از همه خوشحالت می‌کنه؟"
    ],
    "جرئت": [
        "🎯 جرئت: یک تعریف قشنگ از یکی از دوستانت بکن!"
    ],
    "مرسی": [
        "خواهش می‌کنم ❤️",
        "قربون محبتت، موفق باشی 🌹"
    ]
}


def normalize(text):
    text = text.strip().replace("ي", "ی").replace("ك", "ک")
    text = text.replace("‌", " ")
    return " ".join(text.split()).lower().strip("!?؟.,،")


def call_api(method, data=None):
    response = session.post(
        f"{BASE}/{method}",
        json=data or {},
        timeout=25
    )
    response.raise_for_status()
    result = response.json()

    if result.get("status") != "OK":
        print("خطای API:", result)
        return None

    return result.get("data", result)


def answer(text):
    msg = normalize(text)

    # تشخیص عبارت‌های فارسی
    if msg in ("سلام", "سلام ربات", "درود"):
        return random.choice(REPLIES["سلام"])

    if "خوبی" in msg or "خوب هستی" in msg:
        return random.choice(REPLIES["خوبی"])

    if "چطوری" in msg:
        return random.choice(REPLIES["چطوری"])

    if "خداحافظ" in msg or msg == "بای":
        return random.choice(REPLIES["خداحافظ"])

    if msg == "چالش":
        return random.choice(REPLIES["چالش"])

    if msg == "کوییز":
        return random.choice(REPLIES["کوییز"])

    if msg == "حقیقت":
        return random.choice(REPLIES["حقیقت"])

    if msg == "جرئت":
        return random.choice(REPLIES["جرئت"])

    if "مرسی" in msg or "ممنون" in msg:
        return random.choice(REPLIES["مرسی"])

    if msg == "قوانین":
        return (
            "📜 قوانین گروه:\n"
            "۱. احترام به اعضا\n"
            "۲. پرهیز از اسپم\n"
            "۳. رعایت قوانین مدیران"
        )

    if msg == "راهنما":
        return (
            "🛡️ راهنمای گاردتکس:\n"
            "سلام، خوبی، چالش، کوییز، حقیقت، "
            "جرئت، قوانین و خداحافظ"
        )

    return None


def main():
    offset = None
    print("گاردتکس اجرا شد!")

    while True:
        try:
            payload = {"limit": 10}
            if offset:
                payload["offset_id"] = offset

            result = call_api("getUpdates", payload)

            if not result:
                time.sleep(3)
                continue

            for update in result.get("updates", []):
                if not isinstance(update, dict):
                    continue

                chat_id = update.get("chat_id")
                message = update.get("new_message") or {}

                if not chat_id or not isinstance(message, dict):
                    continue

                if message.get("sender_type") == "Bot":
                    continue

                text = message.get("text", "")
                reply = answer(text)

                if reply:
                    call_api("sendMessage", {
                        "chat_id": str(chat_id),
                        "text": reply
                    })

            next_offset = result.get("next_offset_id")
            if next_offset:
                offset = str(next_offset)

            time.sleep(2)

        except Exception as error:
            print("خطا:", error)
            time.sleep(5)


if __name__ == "__main__":
    main()
