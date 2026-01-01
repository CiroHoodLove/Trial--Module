import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import telebot
import os
import random

# --- CONFIG ---
BOT_TOKEN = "8240106331:AAEoxNAZyJR6pxWrhhqyz8lvJEiHjfCfelM"
CHAT_ID = "8050366911"

bot = telebot.TeleBot(BOT_TOKEN)

def get_driver():
    """Setup Chrome to run headlessly but look like a real user."""
    options = uc.ChromeOptions()
    # We don't add '--headless' here because 'xvfb' in the workflow handles the "no screen" part.
    # Adding '--headless' often triggers bot detection.
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1280,960')
    
    driver = uc.Chrome(options=options)
    return driver

def scrape_perchance(driver, prompt):
    print(f"🕵️ Navigating for: {prompt[:15]}...")
    driver.get("https://perchance.org/ai-text-to-image-generator")
    
    try:
        # 1. Switch to the Generator IFrame (Perchance hides the tool inside an iframe)
        # We wait for the iframe to load
        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='ai-text-to-image-generator']"))
        )
        driver.switch_to.frame(iframe)

        # 2. Find Input & Button
        input_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Description']"))
        )
        generate_btn = driver.find_element(By.ID, "generateButtonEl")

        # 3. Type Prompt
        input_box.clear()
        # We add quality boosters automatically
        full_prompt = f"{prompt}, 8k, highly detailed, masterpiece"
        input_box.send_keys(full_prompt)
        time.sleep(1)

        # 4. Click Generate
        driver.execute_script("arguments[0].click();", generate_btn)
        print("⏳ Clicked generate. Waiting for render...")

        # 5. Wait for Image
        # We assume generation takes at least 5 seconds.
        time.sleep(8) 
        
        # We look for the image container. 
        # Note: Selectors on Perchance change occasionally.
        img_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#imageContainer img"))
        )
        
        # Wait until the 'src' is a real URL (not a placeholder)
        for _ in range(10):
            src = img_element.get_attribute("src")
            if src and "http" in src and "googleusercontent" in src: # Perchance images usually hosted here
                return src
            time.sleep(2)
            
        return None

    except Exception as e:
        print(f"❌ Scraping Error: {e}")
        # Take a screenshot if it fails (helper for debugging)
        driver.save_screenshot("debug_error.png")
        return None

def main():
    if not os.path.exists("prompts.txt"):
        print("No prompts.txt!")
        return

    with open("prompts.txt", "r") as f:
        prompts = [line.strip() for line in f if line.strip()]

    print("🚀 Launching Headless Chrome...")
    driver = get_driver()

    try:
        for i, prompt in enumerate(prompts):
            print(f"[{i+1}/{len(prompts)}] Processing: {prompt}")
            
            image_url = scrape_perchance(driver, prompt)
            
            if image_url:
                print("✅ Image found! Downloading...")
                img_data = requests.get(image_url).content
                
                # Send as Document (Uncompressed, No Watermark)
                bot.send_document(
                    CHAT_ID, 
                    img_data, 
                    visible_file_name=f"perchance_gen_{random.randint(1000,9999)}.png",
                    caption=f"Prompt: {prompt}"
                )
                print("📤 Sent to Telegram.")
            else:
                print("⚠️ Failed to extract image.")

            # Cooldown to look human
            time.sleep(5)

    except Exception as e:
        print(f"❌ Critical Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
