# 🧠 MindVault Pro — Secure Smart Notes & Todo Vault

<div align="center">

<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="90" alt="Python"/>

# ✨ MindVault Pro

### Your Personal Digital Brain — Secure Notes, Tasks & Knowledge Vault

<p align="center">
Modern • Fast • Self-Hosted • Mobile Friendly • Beginner Friendly
</p>

<p align="center">

<img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python">
<img src="https://img.shields.io/badge/Flask-Web_App-black?style=for-the-badge&logo=flask">
<img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite">
<img src="https://img.shields.io/badge/Cloudflare-Tunnel-orange?style=for-the-badge&logo=cloudflare">
<img src="https://img.shields.io/badge/Linux-RaspberryPi-red?style=for-the-badge&logo=raspberrypi">
<img src="https://img.shields.io/badge/Termux-Android-green?style=for-the-badge&logo=android">

</p>

---

### 🚀 Live Features

✅ Secure Authentication
✅ Create / Edit / Delete Notes
✅ Smart Todo Management
✅ Responsive UI
✅ Profile System
✅ SQLite Database
✅ Flask Backend
✅ Cloudflare Public Hosting
✅ Works on Windows / Linux / Raspberry Pi / Termux

---

# 📸 Preview

<p align="center">

<img src="https://cdn-icons-png.flaticon.com/512/9068/9068756.png" width="120">
<img src="https://cdn-icons-png.flaticon.com/512/4727/4727424.png" width="120">
<img src="https://cdn-icons-png.flaticon.com/512/3176/3176363.png" width="120">

</p>

---

# 📖 What is MindVault Pro?

MindVault Pro is a modern self-hosted productivity web application where users can:

* Store notes securely
* Manage todos
* Organize knowledge
* Access from anywhere
* Host on Raspberry Pi / VPS / PC
* Make public using Cloudflare Tunnel

Think of it like:

📝 Notion + Todoist + Personal Vault
But fully under YOUR control.

---

# 🛠️ Tech Stack

| Technology        | Purpose           |
| ----------------- | ----------------- |
| Python            | Backend Logic     |
| Flask             | Web Framework     |
| SQLite            | Database          |
| SQLAlchemy        | Database ORM      |
| Flask-Login       | Authentication    |
| Flask-WTF         | Forms & Security  |
| HTML/CSS/JS       | Frontend          |
| Gunicorn          | Production Server |
| Cloudflare Tunnel | Public Hosting    |
| Jinja2            | Dynamic Templates |

---

# 📂 Project Structure

```bash
MindVault-Pro/
│
├── app.py
├── requirements.txt
├── config.py
├── .env
│
├── instance/
│   └── app.db
│
├── templates/
│
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
│
├── routes/
├── models/
├── forms/
└── utils/
```

---

# ⚡ Installation Guide

# 🪟 Windows

## 1️⃣ Install Python

Download:
https://www.python.org/downloads/

⚠️ IMPORTANT:
Enable:

```bash
✅ Add Python to PATH
```

---

## 2️⃣ Clone Repository

```bash
git clone https://github.com/tyagirtk-dev/Pro-Todo.git

cd Pro-Todo
```

---

## 3️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

---

## 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5️⃣ Run Project

```bash
python app.py
```

Open:

```bash
http://127.0.0.1:5000
```

---

# 🐧 Linux / Raspberry Pi

## Install Dependencies

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install python3 python3-pip python3-venv git -y
```

---

## Clone Project

```bash
git clone https://github.com/tyagirtk-dev/Pro-Todo.git

cd Pro-Todo
```

---

## Create VENV

```bash
python3 -m venv venv
```

Activate:

```bash
source venv/bin/activate
```

---

## Install Packages

```bash
pip install -r requirements.txt
```

---

## Run App

```bash
python3 app.py
```

---

# 📱 Android (Termux)

## Install Termux

Download from:
https://f-droid.org/packages/com.termux/

---

## Setup

```bash
pkg update && pkg upgrade -y

pkg install python git -y
```

---

## Clone Project

```bash
git clone https://github.com/tyagirtk-dev/Pro-Todo.git

cd Pro-Todo
```

---

## Setup VENV

```bash
python -m venv venv

source venv/bin/activate
```

---

## Install Requirements

```bash
pip install -r requirements.txt
```

---

## Run

```bash
python app.py
```

---

# 🌍 Make Public Using Cloudflare Tunnel

# Install Cloudflared

## Linux / Raspberry Pi

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb -o cloudflared.deb

sudo dpkg -i cloudflared.deb
```

---

## Start Tunnel

```bash
cloudflared tunnel --url http://localhost:5000
```

---

## Output Example

```bash
https://random-name.trycloudflare.com
```

Now your app is PUBLIC 🌍

---

# 🔐 Security Features

✅ Password Hashing
✅ CSRF Protection
✅ Secure Sessions
✅ Login Authentication
✅ SQL Injection Protection
✅ XSS Protection

---

# 📦 Requirements

```txt
Flask
Flask-SQLAlchemy
Flask-Login
Flask-WTF
WTForms
Flask-Mail
python-dotenv
gunicorn
Pillow
```

Install all:

```bash
pip install -r requirements.txt
```

---

# 🧠 Beginner Explanation

| Component  | Meaning              |
| ---------- | -------------------- |
| Flask      | Main Web App         |
| SQLite     | Stores Notes         |
| Templates  | HTML Pages           |
| Static     | CSS/JS/Images        |
| Routes     | URL Logic            |
| Models     | Database Tables      |
| Forms      | Login/Register Forms |
| Cloudflare | Makes App Public     |

---

# 🚀 Production Deployment

Run using Gunicorn:

```bash
gunicorn app:app
```

---

# 📌 Future Features

* AI Note Assistant
* Voice Notes
* Markdown Editor
* Real-time Collaboration
* Dark Mode
* Mobile App
* Docker Support
* PostgreSQL Support

---

# 🤝 Contributing

Pull requests are welcome.

For major changes:

1. Fork Repository
2. Create Branch
3. Commit Changes
4. Push Branch
5. Open Pull Request

---

# 📜 License

MIT License

---

# ❤️ Author

###  Ritik Singh

Made with ❤️ using Flask & Python

---

# ⭐ Support

If you like this project:

⭐ Star the Repository
🍴 Fork the Project
📢 Share with Friends

---

<div align="center">

# 🚀 MindVault Pro

### Build. Organize. Remember.

</div>
