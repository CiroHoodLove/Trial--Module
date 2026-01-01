import time
import random
import telebot
import os

# --- YOUR CONFIG ---
BOT_TOKEN = "8240106331:AAEoxNAZyJR6pxWrhhqyz8lvJEiHjfCfelM"
CHAT_ID = "8050366911"

bot = telebot.TeleBot(BOT_TOKEN)

def start_generation():
    if not os.path.exists("prompts.txt"):
        print("❌ Error: 'prompts.txt' not found!")
        return

    with open("prompts.txt", "r") as f:
        prompts = [line.strip() for line in f if line.strip()]

    print(f"🚀 Found {len(prompts)} prompts. Speed mode activated.")

    for i, prompt in enumerate(prompts):
        print(f"⚡ [{i+1}/{len(prompts)}] Generating: {prompt}")

        # 1. Create the URL
        seed = random.randint(0, 99999999)
        # We append a random seed so you get a new image every time
        image_url = f"https://pollinations.ai/p/{prompt}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"

        try:
            # 2. Send the URL directly (Fixes IMAGE_PROCESS_FAILED)
            # Telegram servers will fetch the image for you.
            bot.send_photo(
                CHAT_ID, 
                image_url, 
                caption=f"Prompt: {prompt}"
            )
            print("✅ Sent!")

        except Exception as e:
            # If Telegram complains, print it but keep moving
            print(f"❌ Error: {e}")

        # 3. SPEED SETTING
        # Waiting only 5 seconds = 12 images per minute.
        time.sleep(5)

if __name__ == "__main__":
    start_generation()
