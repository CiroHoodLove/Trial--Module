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

def get_image_data(prompt, model="flux"):
    """
    Tries to download the image. 
    If Flux fails/timeouts, it falls back to Turbo (faster).
    """
    seed = random.randint(0, 99999999)
    # ⚠️ REMOVED 'nologo=true' to fix the infinite loading loop
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&seed={seed}&model={model}"
    
    print(f"🔄 Attempting ({model}): {prompt[:15]}...")
    
    try:
        # 30 second timeout for high quality Flux
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200 and len(response.content) > 15000:
            return response.content, seed
        else:
            print(f"⚠️ {model} failed (Size: {len(response.content)} bytes).")
            return None, None
            
    except Exception as e:
        print(f"❌ Error with {model}: {e}")
        return None, None

def process_prompt(prompt):
    clean_prompt = prompt.strip()
    if not clean_prompt: return

    # 1. Try FLUX (High Quality)
    image_data, seed = get_image_data(clean_prompt, model="flux")

    # 2. If Flux failed, force TURBO (Low Quality but Fast)
    if not image_data:
        print(f"⏩ Switching to TURBO for: {clean_prompt[:15]}")
        image_data, seed = get_image_data(clean_prompt, model="turbo")

    # 3. Send if we got anything
    if image_data:
        try:
            filename = f"gen_{seed}.png"
            # SEND AS DOCUMENT (FILE)
            bot.send_document(
                CHAT_ID, 
                image_data, 
                visible_file_name=filename,
                caption=f"Prompt: {clean_prompt}"
            )
            print(f"✅ SENT FILE: {clean_prompt[:15]}")
        except Exception as e:
            print(f"❌ Telegram Send Error: {e}")
    else:
        print(f"💀 Completely failed: {clean_prompt[:15]}")

def run_fast_batch():
    if not os.path.exists("prompts.txt"):
        print("❌ No prompts.txt found")
        return

    with open("prompts.txt", "r") as f:
        prompts = [line.strip() for line in f if line.strip()]

    print(f"🔥 Starting Batch of {len(prompts)} images...")
    
    # 3 WORKERS = Safe Speed. 
    # 5+ workers will get you rate-limited (IP banned) by Pollinations.
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(process_prompt, prompts)

if __name__ == "__main__":
    run_fast_batch()
