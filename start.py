#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

# Color definitions for Kali terminal styling
G = '\033[92m'  # Green
Y = '\033[93m'  # Yellow
R = '\033[91m'  # Red
B = '\033[94m'  # Blue
W = '\033[0m'   # Reset

# Updated with working, live alternatives to replace deleted repositories
TOOLS_CONFIG = {
    "infra": {
        "subfinder": {"repo": "https://github.com/projectdiscovery/subfinder", "type": "go", "apt": "subfinder"},
        "amass": {"repo": "https://github.com/owasp-amass/amass", "type": "go", "apt": "amass"},
        "assetfinder": {"repo": "https://github.com/tomnomnom/assetfinder", "type": "go", "apt": "assetfinder"},
        "theHarvester": {"repo": "https://github.com/laramies/theHarvester", "type": "python"},
        "web-check": {"repo": "https://github.com/lissy93/web-check", "type": "node"}
    },
    "email": {
        "holehe": {"repo": "https://github.com/megadose/holehe", "type": "python"},
        "email-finder": {"repo": "https://github.com/alphatierintel/osint-email-finder", "type": "python"},
        "mosint": {"repo": "https://github.com/gophish/mosint", "type": "go"}
    },
    "username": {
        "sherlock": {"repo": "https://github.com/sherlock-project/sherlock", "type": "python"},
        "whatsmyname": {"repo": "https://github.com/C3n7ral051nt4g3ncy/WhatsMyName-Python", "type": "python"},
        "maigret": {"repo": "https://github.com/soxoj/maigret", "type": "python"}
    },
    "phone": {
        "phoneinfoga": {"repo": "https://github.com/sundowndev/phoneinfoga", "type": "go"},
        "phonesploit-lite": {"repo": "https://github.com/ignis-sec/PhoneSploit-Lite", "type": "python"}
    },
    "intel": {
        "nuclei": {"repo": "https://github.com/projectdiscovery/nuclei", "type": "go", "apt": "nuclei"},
        "dorky": {"repo": "https://github.com/opsdisk/pagodo", "type": "python"}
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
    """Checks tool availability and automates cloning or installation with forced English logs."""
    target_dir = os.path.join("tools", category, tool_name)
    config = TOOLS_CONFIG[category][tool_name]
    
    # Force English output environment execution
    env = os.environ.copy()
    env["LANG"] = "C"
    env["LC_ALL"] = "C"
    env["GIT_TERMINAL_PROMPT"] = "0"

    if "apt" in config:
        if shutil.which(tool_name):
            return True
        print(f"{Y}[*] Installing {tool_name} via APT...{W}")
        subprocess.run(["sudo", "apt", "update", "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
        res = subprocess.run(["sudo", "apt", "install", "-y", config["apt"]], env=env)
        return res.returncode == 0

    if tool_name == "phoneinfoga":
        if shutil.which("phoneinfoga"):
            return True
        print(f"{Y}[*] Installing phoneinfoga via official script...{W}")
        os.makedirs(target_dir, exist_ok=True)
        subprocess.run("curl -sL https://raw.githubusercontent.com/sundowndev/phoneinfoga/master/support/scripts/install | bash", shell=True, cwd=target_dir, env=env)
        if os.path.exists(os.path.join(target_dir, "phoneinfoga")):
            subprocess.run(f"sudo ln -sf $(pwd)/{target_dir}/phoneinfoga /usr/local/bin/phoneinfoga", shell=True, env=env)
        return True

    if os.path.exists(target_dir) and not os.path.exists(os.path.join(target_dir, ".git")):
        shutil.rmtree(target_dir)

    if not os.path.exists(target_dir):
        print(f"{Y}[*] Cloning {tool_name} from GitHub...{W}")
        os.makedirs(os.path.dirname(target_dir), exist_ok=True)
        res = subprocess.run(["git", "clone", config["repo"], target_dir], env=env)
        if res.returncode != 0:
            print(f"{R}[-] Failed to clone {tool_name}. URL is offline or forbidden.{W}")
            return False
            
    return True

def ensure_reports_dir():
    if not os.path.exists("reports"):
        os.makedirs("reports")

# --- MENU ACTIONS ---

def run_infra_recon():
    domain = input(f"{B}[?] Target Domain (e.g., victim.com): {W}").strip()
    if not domain: return
    ensure_reports_dir()
    
    print(f"\n{G}[+] Launching Combined Infrastructure Scan...{W}\n")
    
    if check_and_install_tool("infra", "subfinder"):
        print(f"{Y}[*] Scanning subdomains with Subfinder...{W}")
        with open(f"reports/{domain}_subdomains.txt", "w") as f:
            subprocess.run(["subfinder", "-d", domain], stdout=f)
            
    if check_and_install_tool("infra", "assetfinder"):
        print(f"{Y}[*] Searching additional assets with Assetfinder...{W}")
        with open(f"reports/{domain}_assets.txt", "w") as f:
            subprocess.run(["assetfinder", "--subs-only", domain], stdout=f)

    if check_and_install_tool("infra", "theHarvester"):
        print(f"{Y}[*] Gathering public contacts/IPs via theHarvester...{W}")
        cwd = os.path.join("tools", "infra", "theHarvester")
        if os.path.exists(os.path.join(cwd, "theHarvester.py")):
            subprocess.run(["python3", "theHarvester.py", "-d", domain, "-l", "200", "-b", "anubis,bing,duckduckgo"], cwd=cwd)

    input(f"\n{G}[+] Scans completed. Reports saved to 'reports/'. [ENTER]{W}")

def run_username_recon():
    username = input(f"{B}[?] Target Username: {W}").strip()
    if not username: return
    ensure_reports_dir()
    
    if check_and_install_tool("username", "sherlock"):
        print(f"\n{Y}[*] Launching multi-platform lookup via Sherlock...{W}")
        cwd = os.path.join("tools", "username", "sherlock")
        subprocess.run(["python3", "sherlock", username, "--output", f"../../../reports/{username}_sherlock.txt"], cwd=cwd)
        
    if check_and_install_tool("username", "whatsmyname"):
        print(f"\n{Y}[*] Cross-referencing via WhatsMyName Framework...{W}")
        cwd = os.path.join("tools", "username", "whatsmyname")
        if os.path.exists(os.path.join(cwd, "whatsmyname.py")):
            subprocess.run(["python3", "whatsmyname.py", "-u", username], cwd=cwd)

    input(f"\n{G}[+] Username scans completed. [ENTER]{W}")

def run_email_recon():
    email = input(f"{B}[?] Target Email: {W}").strip()
    if not email: return
    ensure_reports_dir()
    
    if check_and_install_tool("email", "holehe"):
        print(f"\n{Y}[*] Analyzing account registrations with Holehe...{W}")
        cwd = os.path.join("tools", "email", "holehe")
        subprocess.run(["python3", "holehe/modules/social/twitter.py", email], cwd=cwd)
        
    if check_and_install_tool("email", "email-finder"):
        print(f"\n{Y}[*] Gathering email correlations via Email-Finder...{W}")
        cwd = os.path.join("tools", "email", "email-finder")
        if os.path.exists(os.path.join(cwd, "email_finder.py")):
            subprocess.run(["python3", "email_finder.py", "-e", email], cwd=cwd)

    input(f"\n{G}[+] Email investigation completed. [ENTER]{W}")

def run_phone_recon():
    phone = input(f"{B}[?] Target Phone (e.g., +491701234567): {W}").strip()
    if not phone: return
    
    if check_and_install_tool("phone", "phoneinfoga"):
        print(f"\n{Y}[*] Analyzing phone number via PhoneInfoga...{W}")
        subprocess.run(["phoneinfoga", "scan", "-n", phone])
        
    input(f"\n{G}[+] Phone OSINT completed. [ENTER]{W}")

def run_threat_intel():
    domain = input(f"{B}[?] Target Domain for passive intel (e.g., victim.com): {W}").strip()
    if not domain: return
    
    if check_and_install_tool("intel", "nuclei"):
        print(f"\n{Y}[*] Checking exposed technologies passively with Nuclei...{W}")
        subprocess.run(["nuclei", "-u", domain, "-tags", "tech,passive"])
        
    input(f"\n{G}[+] Passive threat intel check completed. [ENTER]{W}")

# --- MAIN MENU ---

def main_menu():
    while True:
        print_banner()
        print(f"{B}[1]{W} Domain & Infrastructure Mapping (subfinder, assetfinder, theHarvester)")
        print(f"{B}[2]{W} Username & Social Media Intelligence (sherlock, whatsmyname)")
        print(f"{B}[3]{W} Email & Leak Analysis (holehe, email-finder)")
        print(f"{B}[4]{W} Phone Number Scanner (phoneinfoga)")
        print(f"{B}[5]{W} Passive Threat Intel (nuclei passive)")
        print(f"-----------------------------------------------------------------")
        print(f"{B}[9]{W} Download/Install all available tools directly")
        print(f"{R}[0]{W} Exit")
        
        choice = input(f"\n{B}Select Option > {W}").strip()
        
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
            print(f"\n{Y}[*] Installing all active categories. This may take a while...{W}")
            for cat, tools in TOOLS_CONFIG.items():
                for tname in tools.keys():
                    check_and_install_tool(cat, tname)
            input(f"\n{G}[+] Setup for all active tools successfully finished! [ENTER]{W}")
        elif choice == "0":
            print(f"\n{G}Exiting framework. Ready for active scope!{W}\n")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{R}[!] Aborted by operator.{W}\n")
        sys.exit(1)
