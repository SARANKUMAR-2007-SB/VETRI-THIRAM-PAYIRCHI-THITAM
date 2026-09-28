# EduGenie — Google Gemini Powered Learning Assistant

A full-stack academic project that combines **Google Gemini**, **Flask**, **SQLite**, HTML/CSS, and JavaScript into a personalized learning workspace.

## Features

- 🔐 Register/Login with password hashing
- 💬 Gemini-powered academic QnA
- 📝 AI summarization
- 🎯 Automatic 3-question MCQ generation
- 🧭 Beginner → advanced learning paths
- 📄 Text-based PDF import for study material
- 📊 Recent activity history
- 🏆 Quiz-result storage
- 📱 Responsive dashboard
- 🔑 Secure server-side API key handling

## Architecture

```text
Browser
  │
  ├── Dashboard UI
  │      ├── QnA
  │      ├── Summary
  │      ├── Quiz
  │      └── Learning Path
  │
  ▼
Flask REST API
  │
  ├── Authentication
  ├── SQLite database
  ├── PDF text extraction
  │
  ▼
GeminiService
  │
  ▼
Google Gemini API
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python, Flask |
| AI | Google Gemini API |
| Database | SQLite |
| PDF | pypdf |
| Authentication | Werkzeug password hashing |
| Configuration | python-dotenv |

## Setup

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/EduGenie.git
cd EduGenie
```

### 2. Virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install

```bash
pip install -r requirements.txt
```

### 4. Environment

Copy `.env.example` to `.env` and set:

```env
GEMINI_API_KEY=YOUR_KEY
GEMINI_MODEL=gemini-2.5-flash
FLASK_SECRET_KEY=YOUR_RANDOM_SECRET
```

Do not commit `.env`.

### 5. Run

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

## Demo Flow

1. Register a new student account.
2. Open the dashboard.
3. Ask: `Explain polymorphism in Java with an example.`
4. Open Summary and paste study material.
5. Open Quiz and paste a passage.
6. Generate exactly 3 MCQs.
7. Open Learning Path.
8. Enter `Spring Boot` and choose `Beginner`.
9. Upload a text-based PDF under Summary and import it.
10. Refresh the dashboard to see recent activity.

## GitHub Commands

```bash
git init
git add .
git commit -m "Initial EduGenie project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/EduGenie.git
git push -u origin main
```

## Security Notes

- Never commit `.env`.
- Never expose the Gemini API key in JavaScript.
- Use a strong `FLASK_SECRET_KEY`.
- For production, use HTTPS and a production WSGI server.
- Add CSRF protection and rate limiting before public deployment.
- PDF extraction is intended for text-based PDFs; scanned PDFs need OCR.

## Academic Modules

### QnA
Uses Gemini to provide context-aware educational explanations.

### Summary
Converts lengthy study material into concise revision notes.

### Quiz
Requests strict JSON and validates that exactly three questions were returned.

### Learning Path
Creates a progressive roadmap based on the learner's selected level.

## Future Scope

- PostgreSQL deployment
- Teacher/admin dashboard
- Student progress analytics
- Flashcard generation
- Voice interaction
- OCR for scanned PDFs
- Adaptive difficulty
- Cloud deployment
- Email notifications
- Course recommendation engine

## License

MIT
