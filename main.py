import requests
import telebot
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor

# --- CONFIG ---
BOT_TOKEN = "8240106331:AAEoxNAZyJR6pxWrhhqyz8lvJEiHjfCfelM"
CHAT_ID = "8050366911"

bot = telebot.TeleBot(BOT_TOKEN)

def get_real_image(url, retries=5):
    """
    Tries to download the image. If it's too small (meaning it's the 
    Pollinations logo/placeholder), it waits and tries again.
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                # CHECK: Is this the real image or the logo?
                # Real images are usually > 50KB. The logo is ~5-10KB.
                if len(response.content) > 20000: 
                    return response.content
                else:
                    print(f"⚠️ Got placeholder logo (Attempt {attempt+1}/{retries}). Waiting...")
                    time.sleep(3) # Wait for server to finish rendering
            else:
                time.sleep(2)
        except Exception as e:
            print(f"Connection error: {e}")
            time.sleep(2)
    return None

def process_prompt(prompt):
    """Generates and sends as a FILE."""
    clean_prompt = prompt.strip()
    if not clean_prompt: return

    print(f"⚙️ Processing: {clean_prompt[:20]}...")
    
    seed = random.randint(0, 99999999)
    # Adding 'nologo=true' and 'enhance=true' for better quality
    image_url = f"https://pollinations.ai/p/{clean_prompt}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"

    # 1. Download the REAL image (skipping the logo)
    image_data = get_real_image(image_url)

    if image_data:
        # 2. Send as DOCUMENT (File)
        try:
            # We give the file a name based on the seed so it looks professional
            file_name = f"flux_gen_{seed}.png"
            
            bot.send_document(
                CHAT_ID, 
                image_data, 
                visible_file_name=file_name
                # No caption added here
            )
            print(f"✅ Sent FILE: {clean_prompt[:20]}")
        except Exception as e:
            print(f"❌ Telegram Upload Error: {e}")
    else:
        print(f"❌ Failed to generate: {clean_prompt[:20]}")

def run_batch():
    if not os.path.exists("prompts.txt"):
        print("No prompts.txt found")
        return

    with open("prompts.txt", "r") as f:
        prompts = [line.strip() for line in f if line.strip()]

    print(f"🔥 Starting Batch: {len(prompts)} images...")
    
    # 3. Parallel Processing (Speed)
    # Lowered workers slightly to 3 to prevent getting the 'Logo' too often
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(process_prompt, prompts)

if __name__ == "__main__":
    run_batch()
