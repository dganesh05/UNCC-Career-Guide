# UNCC Career Guide (protoype)

A comprehensive career guidance and resources platform for UNC Charlotte students and alumni.

## 📋 Overview

UNCC Career Guide helps students find job opportunities, develop professional skills, connect with mentors, and access career resources - all in one platform. From resume building to job searching, we've got you covered.

## 🚀 Features

- **Job Board**: Browse and search job listings from multiple sources
- **Resume Generator**: Create professional resumes with AI assistance
- **Networking Hub**: Connect with professionals and peers
- **Mentorship Hub**: Find and connect with mentors in your field
- **Career Events**: Stay updated with career fairs and other events
- **Resource Library**: Access guides, templates, and tools

## ⚙️ Prerequisites

- **Python 3.8+**
- **Django 4.0+**
- **Virtual Environment** (recommended)

## 💻 Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/your-username/UNCC-Career-Guide.git
cd UNCC-Career-Guide
```

### Step 2: Create and activate a virtual environment

**For Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**For macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Apply database migrations

```bash
python manage.py migrate
```

## 🏃‍♂️ Running the application

Start the development server:

```bash
python manage.py runserver
```

Access the application at: http://127.0.0.1:8000/

## 📁 Project Structure

- `base/`: Core application with common features
- `resume_generator/`: Resume building functionality
- `templates/`: HTML templates for the application
- `uncc_career_guide/`: Project settings and main URL configuration

## 📝 License

This project is licensed under the [MIT License](LICENSE).
