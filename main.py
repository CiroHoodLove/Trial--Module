import time
import random
import requests
import telebot
import os

# --- HARDCODED CONFIGURATION ---
BOT_TOKEN = "8240106331:AAEoxNAZyJR6pxWrhhqyz8lvJEiHjfCfelM"
CHAT_ID = "8050366911"

# Initialize Bot
bot = telebot.TeleBot(BOT_TOKEN)

def start_generation():
    # 1. Check if prompts.txt exists
    if not os.path.exists("prompts.txt"):
        print("❌ Error: 'prompts.txt' not found in the folder!")
        return

    # 2. Read the prompts
    with open("prompts.txt", "r") as f:
        prompts = [line.strip() for line in f if line.strip()]

    print(f"🚀 Found {len(prompts)} prompts. Target: ~100 images/hour.")

    # 3. Process each prompt
    for i, prompt in enumerate(prompts):
        print(f"🖼️ [{i+1}/{len(prompts)}] Generating: {prompt}")

        # Generate a random seed for unique results
        seed = random.randint(0, 99999999)
        
        # Flux.1 Model via Pollinations
        image_url = f"https://pollinations.ai/p/{prompt}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"

        try:
            # Download image from Pollinations
            response = requests.get(image_url, timeout=60)
            
            if response.status_code == 200:
                # Send to your Telegram
                bot.send_photo(
                    CHAT_ID, 
                    response.content, 
                    caption=f"✅ **Prompt:** {prompt}\n🤖 Model: Flux.1",
                    parse_mode="Markdown"
                )
                print("📤 Image sent to Telegram!")
            else:
                print(f"⚠️ Failed to generate. Status code: {response.status_code}")

        except Exception as e:
            print(f"❌ Error during process: {e}")

        # 4. Rate Limiting (Crucial for 100/hour)
        # 3600 seconds / 100 images = 36 seconds per image.
        # We wait 40 seconds to stay safely within limits.
        if i < len(prompts) - 1: # Don't wait after the very last image
            print("⏳ Waiting 40 seconds before next prompt...")
            time.sleep(40)

    print("🏁 Finished all prompts!")

if __name__ == "__main__":
    start_generation()
