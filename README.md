# AdvoSphere: AI Legal Assistant

AdvoSphere is a complete, portfolio-grade AI-powered Legal Assistant web application designed to help citizens understand their statutory rights, draft formal legal documents, audit contracts, and request information from public authorities.

This application is built with a lightweight, secure stack utilizing **Flask (Python)**, **SQLite**, **Vanilla HTML5/CSS3/JavaScript**, and the **Google Gemini API**.

---

## 🌟 Key Features

1. **AI Legal Chatbot (AdvoBot)**:
   - ChatGPT-style responsive layout.
   - Interactive legal questions and answers powered by Gemini API.
   - Bookmarking (saving) important responses and deleting chats.
   - Live query history searching in the sidebar.
   - Full history PDF exports.
   - Response feedback ratings (1-5 stars) and comments.

2. **Legal Rights Finder**:
   - Analyzes real-world grievances (e.g. unpaid salary, defective products).
   - Maps situation details to consumer/labor/civil rights.
   - Provides step-by-step recommended next actions.

3. **Notice Builder**:
   - Dynamic templates for: Consumer Complaints, Salary Recovery, RTI Applications, Cybercrime Reports, and Property Disputes.
   - Interactive UI forms loading custom fields for each category.
   - Real-time on-screen notice draft editing.
   - Clipboard copy and print-ready PDF compilations.

4. **Document Auditor (Analyzer)**:
   - Safe drag-and-drop uploads for `.pdf` and `.docx` files.
   - In-memory text extraction and structured parsing.
   - Extracts executive summaries, key obligations, penalties, and translates legalese to simple terms.

5. **RTI Assistant**:
   - Complete guides for standard filing, First Appeals, and Second Appeals.
   - Copyable templates and process explanations.
   - Expandable FAQ accordion sections.

6. **Admin Dashboard Control**:
   - Overview metrics: total accounts, active chat sessions, drafts compiled, average feedback rating.
   - User Management: list all accounts, toggle administrative access, delete accounts.
   - Logs: review all chatbot comments and star ratings.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, Vanilla CSS3 (Custom design system, variables, dark/light themes, layouts), Vanilla JavaScript (AJAX communications, local theme storage, markdown compiler).
- **Backend**: Python 3.13+, Flask Web Framework (Blueprint architectures).
- **Database**: SQLite3 (No external setup required, initialized automatically).
- **AI Engine**: Google Gemini API (`gemini-1.5-flash`).
- **File Utilities**: ReportLab (PDF compilation), PyPDF (PDF text reader), python-docx (DOCX reader).

---

## ⚙️ Setup and Installation Guide

Follow these steps to run the application locally on your machine:

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your system. You can verify this by running:
```bash
py --version  # Windows
# or
python3 --version  # macOS/Linux
```

### 2. Clone or Copy Project Files
Place the project directory in your working directory. Ensure the following folder structure is visible:
```
AI-Legal-Assistant/
├── app.py
├── config.py
├── requirements.txt
├── .env.template
├── models/
├── routes/
├── services/
├── static/
├── templates/
├── utils/
└── tests/
```

### 3. Install Dependencies
Run pip to install all the required Python libraries listed in `requirements.txt`:
```bash
py -m pip install -r requirements.txt  # Windows
# or
pip3 install -r requirements.txt  # macOS/Linux
```

### 4. Configure Environment Variables
1. Copy the `.env.template` file to a new file named `.env`:
   ```bash
   copy .env.template .env  # Windows
   # or
   cp .env.template .env  # macOS/Linux
   ```
2. Open `.env` and fill in your details:
   - Generate a secure string for `FLASK_SECRET_KEY` (used for session encryption).
   - Enter your **Google Gemini API Key** under `GEMINI_API_KEY`.
     * *Note: If no API key is specified, the application will automatically enter **Simulator Mode** allowing you to test all UI flows, notice forms, upload audits, and chats using local simulated legal rules.*

#### Obtaining a Gemini API Key:
- Go to the [Google AI Studio](https://aistudio.google.com/).
- Sign in with your Google account.
- Click on **Create API Key**.
- Copy the key and paste it directly into your `.env` file:
  ```env
  GEMINI_API_KEY=AIzaSyD...
  ```

---

## 🚀 Running the Application

Start the local Flask development server:
```bash
py app.py  # Windows
# or
python3 app.py  # macOS/Linux
```

The terminal will print confirmation details:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```
Open your browser and navigate to **`http://127.0.0.1:5000`** to interact with the application.

---

## 🧪 Running Unit Tests
To run the automated validation tests (checking registration validation, database crud tables, and validators):
```bash
py -m unittest discover -s tests  # Windows
# or
python3 -m unittest discover -s tests  # macOS/Linux
```

---

## 🛡️ Administrative Accounts
For evaluation, the application seeds a default Administrator account on startup if the database is clean:
- **Email**: `admin@legalassistant.com`
- **Password**: `adminpassword`

Login with these credentials to review user directories, toggle roles, and view submitted feedback logs.

---

## 🔒 Security Practices
- **Password Protection**: User passwords are never saved in plain text; they are hashed using secure SHA-256 PBKDF2 algorithms via `werkzeug.security`.
- **Upload Safety**: Uploaded documents are audited in-memory. Files are parsed, and the local files are immediately cleaned from the filesystem after analysis.
- **SQL Injection Safeguards**: All database interactions utilize parameterized query methods (`?` placeholders) in SQLite.
