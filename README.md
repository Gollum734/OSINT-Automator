# OSINT Automator 

A modular Python wrapper designed for penetration testers to automate the passive reconnaissance phase. This tool structures, installs, and runs 14 elite open-source OSINT utilities directly from a single interactive CLI menu.

## 📁 Repository Structure
```text
OSINT-Automator/
├── start.py                # Main controller & interactive menu
├── requirements.txt         # Core Python dependencies
├── .gitignore               # Keeps your repo clean from reports/tools
└── tools/                  # Managed sub-directories for cloned tools
    ├── infra/
    ├── email/
    ├── username/
    └── phone/
