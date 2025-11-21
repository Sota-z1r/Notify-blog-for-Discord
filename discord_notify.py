from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from discord_webhook import DiscordWebhook
import time

# =============================
# 設定
# =============================
BLOG_URL = "https://www.nogizaka46.com/s/n46/diary/MEMBER"
DISCORD_WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"
CHECK_INTERVAL = 60  # 秒

# =============================
# Selenium設定
# =============================
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())

def get_latest_blog():
    """最新ブログ1件の情報を取得"""
    chrome = webdriver.Chrome(service=service, options=options)
    chrome.get(BLOG_URL)
    time.sleep(10)  # JS読み込み待機（重要）

    # ブログ1件分のブロックを取得
    block = chrome.find_element(By.CSS_SELECTOR, "div.m--postone.a--op.js-pos.is-v")

    # 各情報をブロック内から取得
    title = block.find_element(By.CLASS_NAME, "m--postone__ttl").text
    member = block.find_element(By.CLASS_NAME, "m--postone__name").text
    date = block.find_element(By.CLASS_NAME, "m--postone__time").text
    link = block.find_element(By.CSS_SELECTOR, "a.m--postone__a.hv--thumb").get_attribute("href")

    chrome.quit()
    return {"title": title, "member": member, "date": date, "link": link}

def send_discord_notification(blog):
    """Discord通知送信"""
    message = (
        f"📢【乃木坂46ブログ更新】\n"
        f"👤 {blog['member']}\n"
        f"🕒 {blog['date']}\n"
        f"📝 {blog['title']}\n"
        f"🔗 {blog['link']}"
    )
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=message)
    webhook.execute()

# =============================
# メイン処理
# =============================
if __name__ == "__main__":
    print("=== 初回取得 ===")
    latest = get_latest_blog()
    print(latest)

    last_date = latest["date"]

    while True:
        time.sleep(CHECK_INTERVAL)
        try:
            new_blog = get_latest_blog()
            if new_blog["date"] != last_date:
                print("🔔 新しい投稿を検知しました！")
                send_discord_notification(new_blog)
                last_date = new_blog["date"]
            else:
                print("（変化なし）", new_blog["date"])
        except Exception as e:
            print("⚠️ エラー:", e)
