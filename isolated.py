#!/usr/bin/env python3
import os, sys, platform, time, math, webbrowser, requests, base64

# ──────────────────────────────────────────────────────────────
#  VANTAGE UI - SECURITY & CONFIG
# ──────────────────────────────────────────────────────────────
# Replace with your Raw GitHub/Pastebin link for remote keys
API_URL = "https://raw.githubusercontent.com/youruser/yourrepo/main/keys.txt"
VERSION = "6.5.0-SECURE"
CREDIT = "MADE BY ISOLATED"

# Base64 encoded "moggedui"
SECRET_VAL = "bW9nZ2VkdWk=" 

class c:
    R = "\033[0m"; B = "\033[1m"; D = "\033[2m"
    C = "\033[96m"; G = "\033[92m"; Y = "\033[93m"
    M = "\033[95m"; R1 = "\033[91m"

def clr(): 
    os.system("cls" if platform.system() == "Windows" else "clear")

def get_master():
    # Decodes the hidden master key
    return base64.b64decode(SECRET_VAL).decode('utf-8')

def get_rainbow(i, speed=0.1):
    t = (time.time() * speed * 10) + (i * 0.2)
    r = int(127 * math.sin(t) + 128)
    g = int(127 * math.sin(t + 2 * math.pi / 3) + 128)
    b = int(127 * math.sin(t + 4 * math.pi / 3) + 128)
    return f"\033[38;2;{r};{g};{b}m"

# ──────────────────────────────────────────────────────────────
#  UI ASSETS & CATEGORIES
# ──────────────────────────────────────────────────────────────
CAT_ICON_1 = [
    "          ⢤⣶⣄          ",
    "    ⣀⣤⡾⠿⢿⡀    ⣠⣶⣿⣷    ",
    "⢀⣴⣦⣴⣿⡋  ⠈⢳⡄⢠⣾⣿⠁⠈⣿⡆  ",
    "⣰⣿⣿⠿⠛⠉⠉⠁  ⠹⡄⣿⣿⣿  ⢹⡇  "
]

CAT_ICON_2 = [
    "      ⢀⣀⣤⡎      ",
    "  ⣰⢾⠓⠛⠉⢉⡽⠀⣧    ",
    "⢀⣴⢿⣲⣤⣤⡤⡏  ⣆   ",
    "⢨⠏  ⣁⡼⠁⢱⡀  ⢦⣀"
]

CAT_ICON_3 = [
    "    ⢀⣤⣄      ",
    "  ⢰⣿⣿⣿⣿⡆ ⣠⣶⣿⣶⡀",
    "  ⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿",
    "    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏"
]

CATEGORIES = [
    {
        "name": "PENETRATION & NETWORK",
        "icon": CAT_ICON_1,
        "tools": [
            ("10", "Anonymity Hiding Tools", "https://github.com/Und3rf0ll0w/anon-surf"),
            ("20", "Information Gathering", "https://nmap.org/"),
            ("30", "Wireless Attack Tools", "https://wifiphisher.org/"),
            ("40", "SQL Injection Tools", "https://sqlmap.org/"),
            ("50", "Phishing Attack Tools", "https://github.com/trustedsec/social-engineer-toolkit")
        ]
    },
    {
        "name": "SOCIAL & SYSTEM",
        "icon": CAT_ICON_2,
        "tools": [
            ("60", "Web & XSS Attack Tools", "https://github.com/hahwul/dalfox"),
            ("70", "Payload Creation Tools", "https://github.com/Screetsec/TheFatRat"),
            ("80", "Forensics & Reverse", "https://www.wireshark.org/"),
            ("90", "Exploit Framework", "https://github.com/threat9/routersploit"),
            ("11", "Android Hacking Tools", "https://github.com/thelinuxchoice/lockphish")
        ]
    },
    {
        "name": "OATHNET INTELLIGENCE",
        "icon": CAT_ICON_3,
        "tools": [
            ("15", "OSINT Framework Tree", "https://osintframework.com/"),
            ("ON", "Oathnet Intelligence Hub", "https://oathnet.io/"),
            ("DL", "Oathnet Data Leaks Search", "https://oathnet.io/leaks"),
            ("SI", "Oathnet Stealer Intel", "https://oathnet.io/stealer")
        ]
    }
]

# ──────────────────────────────────────────────────────────────
#  CORE AUTH & LOADING
# ──────────────────────────────────────────────────────────────
def verify_access():
    clr()
    master_key = get_master() #
    print(f"\n{c.B}{c.C}── VANTAGE REMOTE AUTH ──{c.R}".center(60))
    key_input = input(f"\n  {c.D}[{c.C}?{c.D}]{c.R} ENTER API KEY: ").strip()

    if key_input == master_key: #
        print(f"  {c.G}[+] Master Bypass Authorized.{c.R}")
        time.sleep(1); return True

    try:
        r = requests.get(API_URL, timeout=5)
        if key_input in r.text.splitlines():
            print(f"  {c.G}[+] API Key Verified.{c.R}")
            time.sleep(1); return True
    except:
        print(f"  {c.Y}[!] Server Offline. Local Auth Only.{c.R}")

    print(f"  {c.R1}[-] Invalid Key.{c.R}"); time.sleep(2); return False

def loading_seq():
    clr()
    for step in ["SYNCING", "DECRYPTING", "LOADING HUB"]:
        for i in range(11):
            bar = "█" * i + "░" * (10 - i)
            sys.stdout.write(f"\r  {c.C}[ {bar} ] {step}... {i*10}%")
            sys.stdout.flush(); time.sleep(0.04)
        print()

def draw_interface():
    clr()
    print("\n" + f"{c.B}{c.C}{CREDIT.center(65)}{c.R}") #
    print("—"*65)
    print(f" VANTAGE | [ STATUS ] {c.G}AUTH_OK{c.R} | [ VER ] {VERSION}".center(75))
    print("—"*65 + "\n")
    
    for cat in CATEGORIES:
        for i, line in enumerate(cat["icon"]):
            rainbow_line = "".join([f"{get_rainbow(i+j)}{char}" for j, char in enumerate(line)])
            print(rainbow_line.center(75))
        print(f"\n{c.B}{c.C}[ {cat['name']} ]{c.R}".center(70))
        for key, name, url in cat["tools"]:
            print(f"{c.D}[{c.C}{key}{c.D}]{c.R} {name}".center(65))
        print("\n")

def main():
    if platform.system() == "Windows": os.system("color")
    if not verify_access(): sys.exit()
    loading_seq()
    
    while True:
        draw_interface()
        print(f"  {c.D}[{c.R1}00{c.D}]{c.R} Exit".center(65))
        cmd = input(f"\n  {c.M} vtg@phantom ~# {c.R}").strip().upper()
        
        if cmd in ["0", "00"]: break
        for cat in CATEGORIES:
            for key, name, url in cat["tools"]:
                if cmd == key.upper():
                    webbrowser.open(url)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit()