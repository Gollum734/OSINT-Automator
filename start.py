#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

# Farb-Definitionen für Kali Terminal-Optik
G = '\033[92m'  # Grün
Y = '\033[93m'  # Gelb
R = '\033[91m'  # Rot
B = '\033[94m'  # Blau
W = '\033[0m'   # Reset

# Konfiguration aller 14 Tools
TOOLS_CONFIG = {
    "infra": {
        "subfinder": {"repo": "https://github.com/projectdiscovery/subfinder", "type": "go", "apt": "subfinder"},
        "amass": {"repo": "https://github.com/owasp-amass/amass", "type": "go", "apt": "amass"},
        "assetfinder": {"repo": "https://github.com/tomnomnom/assetfinder", "type": "go", "apt": "assetfinder"},
        "theHarvester": {"repo": "https://github.com/laramies/theHarvester", "type": "python", "req": "requirements.txt"},
        "web-check": {"repo": "https://github.com/lissy93/web-check", "type": "node"}
    },
    "email": {
        "holehe": {"repo": "https://github.com/megadose/holehe", "type": "python", "setup": "setup.py"},
        "email2phone": {"repo": "https://github.com/sundowndev/email2phone", "type": "python", "req": "requirements.txt"},
        "infoga": {"repo": "https://github.com/m4ll0k/Infoga", "type": "python", "req": "requirements.txt"}
    },
    "username": {
        "sherlock": {"repo": "https://github.com/sherlock-project/sherlock", "type": "python", "req": "requirements.txt"},
        "whatsmyname": {"repo": "https://github.com/Goldennomad/WhatsMyName", "type": "python", "req": "requirements.txt"},
        "maigret": {"repo": "https://github.com/soxoj/maigret", "type": "python", "setup": "setup.py"}
    },
    "phone": {
        "phoneinfoga": {"repo": "https://github.com/sundowndev/phoneinfoga", "type": "go", "apt": "phoneinfoga"}
    },
    "intel": {
        "nuclei": {"repo": "https://github.com/projectdiscovery/nuclei", "type": "go", "apt": "nuclei"},
        "dorky": {"repo": "https://github.com/sushil79/dorky", "type": "python", "req": "requirements.txt"}
    }
}

def print_banner():
    os.system('clear')
    print(f"""{B}
    ██╗  ██╗██╗  ████████╗██╗███╗   ███╗ █████╗ ████████╗██████╗ 
    ██║  ██║██║  ╚══██╔══╝██║████╗ ████║██╔══██╗╚══██╔══╝██╔══██╗
    ██║  ██║██║     ██║   ██║██╔████╔██║███████║   ██║   ██████╔╝
    ██║  ██║██║     ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██╔══██╗
    ╚█████╔╝███████╗██║   ██║██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║
     ╚════╝ ╚══════╝╚═╝   ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
                    {Y}[ Ultimate OSINT Framework ]{W}
    """)

def check_and_install_tool(category, tool_name):
    """Prüft Verfügbarkeit und automatisiert die Installation via Apt oder Git-Klon."""
    target_dir = os.path.join("tools", category, tool_name)
    
    # Check 1: Über APT installierte System-Tools
    if "apt" in TOOLS_CONFIG[category][tool_name]:
        if shutil.which(tool_name):
            return True
        else:
            print(f"{Y}[*] {tool_name} wird via APT installiert...{W}")
            subprocess.run(["sudo", "apt", "update", "-y"], stdout=subprocess.DEVNULL)
            res = subprocess.run(["sudo", "apt", "install", "-y", TOOLS_CONFIG[category][tool_name]["apt"]])
            return res.returncode == 0

    # Check 2: Git-Repositories klonen und einrichten
    if not os.path.exists(target_dir):
        print(f"{Y}[*] Klone {tool_name} aus GitHub...{W}")
        os.makedirs(os.path.dirname(target_dir), exist_ok=True)
        res = subprocess.run(["git", "clone", TOOLS_CONFIG[category][tool_name]["repo"], target_dir])
        if res.returncode != 0:
            return False
        
        config = TOOLS_CONFIG[category][tool_name]
        if "req" in config:
            print(f"{Y}[*] Installiere Python-Abhängigkeiten für {tool_name}...{W}")
            subprocess.run(["pip3", "install", "-r", os.path.join(target_dir, config["req"])], stdout=subprocess.DEVNULL)
        elif "setup" in config:
            print(f"{Y}[*] Führe Python-Build aus...{W}")
            subprocess.run(["python3", os.path.join(target_dir, config["setup"]), "install"], stdout=subprocess.DEVNULL)
            
    return True

def ensure_reports_dir():
    if not os.path.exists("reports"):
        os.makedirs("reports")

# --- MENÜ-AKTIONEN ---

def run_infra_recon():
    domain = input(f"{B}[?] Target Domain (z.B. victim.com): {W}").strip()
    if not domain: return
    ensure_reports_dir()
    
    print(f"\n{G}[+] Starte Infrastruktur-Kombinations-Scan...{W}\n")
    
    if check_and_install_tool("infra", "subfinder"):
        print(f"{Y}[*] Scanne Subdomains mit Subfinder...{W}")
        with open(f"reports/{domain}_subdomains.txt", "w") as f:
            subprocess.run(["subfinder", "-d", domain], stdout=f)
            
    if check_and_install_tool("infra", "assetfinder"):
        print(f"{Y}[*] Suche zusätzliche Assets mit Assetfinder...{W}")
        with open(f"reports/{domain}_assets.txt", "w") as f:
            subprocess.run(["assetfinder", "--subs-only", domain], stdout=f)

    if check_and_install_tool("infra", "theHarvester"):
        print(f"{Y}[*] Suche öffentliche Kontakte/IPs mit theHarvester...{W}")
        cwd = os.path.join("tools", "infra", "theHarvester")
        subprocess.run(["python3", "theHarvester.py", "-d", domain, "-l", "200", "-b", "anubis,bing,duckduckgo"], cwd=cwd)

    input(f"\n{G}[+] Scans beendet. Berichte liegen im Ordner 'reports/'. [ENTER]{W}")

def run_username_recon():
    username = input(f"{B}[?] Target Username: {W}").strip()
    if not username: return
    ensure_reports_dir()
    
    if check_and_install_tool("username", "sherlock"):
        print(f"\n{Y}[*] Starte Multi-Plattform-Abgleich über Sherlock...{W}")
        cwd = os.path.join("tools", "username", "sherlock")
        subprocess.run(["python3", "sherlock.py", username, "--output", f"../../../reports/{username}_sherlock.txt"], cwd=cwd)
        
    if check_and_install_tool("username", "whatsmyname"):
        print(f"\n{Y}[*] Gegenprüfung über WhatsMyName Datenbank...{W}")
        cwd = os.path.join("tools", "username", "whatsmyname")
        # WhatsMyName nutzt ein zentrales Erkennungsskript
        if os.path.exists(os.path.join(cwd, "whatsmyname", "main.py")):
            subprocess.run(["python3", "whatsmyname/main.py", "-u", username], cwd=cwd)

    input(f"\n{G}[+] Profil-Scans abgeschlossen. [ENTER]{W}")

def run_email_recon():
    email = input(f"{B}[?] Target Email: {W}").strip()
    if not email: return
    ensure_reports_dir()
    
    if check_and_install_tool("email", "holehe"):
        print(f"\n{Y}[*] Analysiere Account-Registrierungen mit Holehe...{W}")
        subprocess.run(["holehe", email])
        
    if check_and_install_tool("email", "infoga"):
        print(f"\n{Y}[*] Suche Leak-Kontexte über Infoga...{W}")
        cwd = os.path.join("tools", "email", "infoga")
        subprocess.run(["python3", "infoga.py", "-t", email], cwd=cwd)

    input(f"\n{G}[+] E-Mail-Untersuchung beendet. [ENTER]{W}")

def run_phone_recon():
    phone = input(f"{B}[?] Target Phone (z.B. +491701234567): {W}").strip()
    if not phone: return
    
    if check_and_install_tool("phone", "phoneinfoga"):
        print(f"\n{Y}[*] Analysiere Rufnummer über PhoneInfoga...{W}")
        subprocess.run(["phoneinfoga", "scan", "-n", phone])
        
    input(f"\n{G}[+] Telefon-OSINT beendet. [ENTER]{W}")

def run_threat_intel():
    domain = input(f"{B}[?] Target Domain für Passiv-Intel (z.B. victim.com): {W}").strip()
    if not domain: return
    
    if check_and_install_tool("intel", "nuclei"):
        print(f"\n{Y}[*] Prüfe exponierte Technologien passiv mit Nuclei...{W}")
        subprocess.run(["nuclei", "-u", domain, "-tags", "tech,passive"])
        
    input(f"\n{G}[+] Passiver Intel-Check abgeschlossen. [ENTER]{W}")

# --- HAUPTMENÜ ---

def main_menu():
    while True:
        print_banner()
        print(f"{B}[1]{W} Domain & Infrastruktur Mapping (subfinder, assetfinder, theHarvester)")
        print(f"{B}[2]{W} Username & Social Media Spionage (sherlock, whatsmyname)")
        print(f"{B}[3]{W} E-Mail & Leak-Analyse (holehe, infoga)")
        print(f"{B}[4]{W} Telefonnummern-Scanner (phoneinfoga)")
        print(f"{B}[5]{W} Passive Threat Intel (nuclei passive)")
        print(f"-----------------------------------------------------------------")
        print(f"{B}[9]{W} Alle 14 Tools direkt vollständig herunterladen/installieren")
        print(f"{R}[0]{W} Exit")
        
        choice = input(f"\n{B}Auswahl > {W}").strip()
        
        if choice == "1":
            run_infra_recon()
        elif choice == "2":
            run_username_recon()
        elif choice == "3":
            run_email_recon()
        elif choice == "4":
            run_phone_recon()
        elif choice == "5":
            run_threat_intel()
        elif choice == "9":
            print(f"\n{Y}[*] Installiere alle Kategorien. Das kann dauern...{W}")
            for cat, tools in TOOLS_CONFIG.items():
                for tname in tools.keys():
                    check_and_install_tool(cat, tname)
            input(f"\n{G}[+] Setup für alle Tools abgeschlossen! [ENTER]{W}")
        elif choice == "0":
            print(f"\n{G}Abgeschlossen. Bereit für den aktiven Scope!{W}\n")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{R}[!] Abgebrochen vom Operator.{W}\n")
        sys.exit(1)
