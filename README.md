Ultimate OSINT Automator

A modular Python wrapper designed for penetration testers to automate the passive reconnaissance phase. This tool structures, installs, and runs 14 elite open-source OSINT utilities directly from a single interactive CLI menu.
📁 Repository Structure
Plaintext

    OSINT-Automator/
    ├── start.py                # Main controller & interactive menu
    ├── requirements.txt         # Core Python dependencies
    ├── .gitignore               # Keeps your repo clean from reports/tools
    └── tools/                  # Managed sub-directories for cloned tools
        ├── infra/
        ├── email/
        ├── username/
        └── phone/

🛠️ Included Tools

    Infrastructure: subfinder, amass, assetfinder, theHarvester, web-check

    Email & Leaks: holehe, email2phone, infoga

    Usernames: sherlock, whatsmyname, maigret

    Phone: phoneinfoga

    Threat Intel & Dorks: nuclei, dorky

🚀 Installation & Usage

Clone this repository and run the script. The framework will automatically handle the missing dependencies and clone all tools upon their first execution.

    git clone https://github.com//OSINT-Automator.git
    cd YOUR-REPO-NAME
    pip3 install -r requirements.txt
    chmod +x start.py
    ./start.py

⚠️ Disclaimer

This tool is for educational purposes and authorized penetration testing only. Always ensure you have explicit permission before conducting any reconnaissance activities.
