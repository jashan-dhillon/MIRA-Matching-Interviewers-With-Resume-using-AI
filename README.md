# MIRA DRDO - Recruitment and Assessment System

<p align="center">
  <strong>🔬 MIRA - Manpower Intelligence & Recruitment Automation</strong>
  <br>
  <em>Recruitment and Assessment Centre, DRDO</em>
  <br>
  Department of Defence Research and Development | Ministry of Defence, Government of India
</p>

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Technology Stack](#-technology-stack)
3. [Project Structure](#-project-structure)
4. [Getting Started](#-getting-started)
5. [AI Features](#-ai-features)
6. [API Reference](#-api-reference)
7. [User Roles & Access](#-user-roles--access)
8. [Database Schema](#-database-schema)
9. [Troubleshooting](#-troubleshooting)

---

## 🎯 Project Overview

**MIRA (Manpower Intelligence & Recruitment Automation)** is a web-based recruitment and assessment management system designed for DRDO's Recruitment and Assessment Centre (RAC). The system streamlines the process of:

- **Managing recruitment advertisements** - Create, update, and track job advertisements
- **AI-powered expert panel formation** - Automatically score and recommend experts using LLM + embeddings
- **Interview board generation** - Create interview panels with AI relevance analysis
- **Formal PDF invitations** - Auto-generate DRDO-style invitation letters attached to emails
- **Expert email notifications** - Automated email invitations with PDF attachments when boards are finalized
- **User authentication & authorization** - Role-based access for admins, experts, and candidates

### Key Features

| Feature | Description |
|---------|-------------|
| **Advertisement Management** | Create and manage recruitment advertisements with multiple items |
| **Expert Database** | Maintain a database of 17+ experts with AI-computed relevance scores |
| **AI-Powered Panel Generation** | Auto-suggest experts using cosine similarity + Ollama LLM scoring |
| **PDF Invitation Letters** | Formal DRDO-style PDF invitations auto-generated and emailed to experts |
| **Panel Generation** | Create interview panels with chairperson, departmental, and external experts |
| **Role-Based Access Control** | Different access levels for Admin, Expert, and Candidate roles |
| **Secure Authentication** | CAPTCHA-protected login and signup with bcrypt password hashing |

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │◄───►│   Flask API     │◄───►│   MongoDB       │
│   (HTML/CSS/JS) │     │   (Python)      │     │   Database      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
              ┌─────┴─────┐        ┌─────┴─────┐
              │  Ollama   │        │ Sentence  │
              │  LLM      │        │Transformers│
              │(llama3.2) │        │(MiniLM-L6)│
              └───────────┘        └───────────┘
```

---

## 🛠 Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Backend runtime |
| Flask | 3.0.0 | Web framework |
| PyMongo | 4.6.1 | MongoDB driver |
| Flask-CORS | 4.0.0 | Cross-Origin Resource Sharing |
| bcrypt | 4.1.2 | Password hashing |
| python-dotenv | 1.0.0 | Environment variables |

### AI / ML
| Technology | Purpose |
|------------|---------|
| Ollama (llama3.2) | Local LLM for expert relevance scoring & reasoning |
| sentence-transformers | Text embeddings (all-MiniLM-L6-v2) |
| scikit-learn | Cosine similarity calculations |
| fpdf2 | PDF invitation letter generation |

### Frontend
| Technology | Purpose |
|------------|---------|
| HTML5 | Page structure |
| CSS3 | Styling (custom + Poppins font) |
| Vanilla JavaScript | Client-side logic |
| Font Awesome 6.5.1 | Icons |

### Database & Infrastructure
| Technology | Purpose |
|------------|---------|
| MongoDB | NoSQL document database |
| Gmail SMTP | Email delivery for expert invitations |

---

## 📁 Project Structure

```
MIRA-3Feb/
├── 📄 app.py                    # Main Flask application entry point
├── 📄 requirements.txt          # Python dependencies
├── 📄 .env.example              # Environment variables template
├── 📄 README.md                 # This documentation
├── 📄 advt_156.pdf              # Sample advertisement PDF
│
├── 📁 ai/                       # AI Modules
│   ├── __init__.py              # Module exports
│   ├── embedding_generator.py   # Text embedding generation (MiniLM-L6-v2)
│   ├── panel_generator.py       # Optimal panel generation algorithm
│   ├── relevance_scorer.py      # Expert relevance scoring with LLM
│   ├── similarity_calculator.py # Cosine similarity + Ollama LLM calls
│   └── pdf_extractor.py         # PDF text extraction for advertisements
│
├── 📁 routes/                   # API Route Blueprints
│   ├── __init__.py
│   ├── auth_routes.py           # Authentication endpoints
│   ├── admin_routes.py          # Admin & seed endpoints
│   ├── advertisement_routes.py  # Advertisement CRUD
│   ├── item_routes.py           # Item CRUD + board completion + email
│   ├── expert_routes.py         # Expert CRUD
│   ├── panel_routes.py          # Panel management
│   ├── pdf_routes.py            # PDF upload & extraction
│   └── matching_routes.py       # AI matching & scoring endpoints
│
├── 📁 utils/                    # Utility Modules
│   ├── email_sender.py          # Gmail SMTP email with PDF attachment
│   └── pdf_invitation.py        # DRDO formal PDF invitation generator
│
├── 📁 fe/                       # Frontend - HTML Pages
│   ├── login.html               # Login/Signup page
│   ├── home.html                # Dashboard homepage
│   ├── admin.html               # Admin dashboard
│   ├── advertisment.html        # Advertisement details
│   ├── item.html                # Item/Board generation page (AI panel)
│   ├── experts.html             # Experts directory
│   ├── expert_home.html         # Expert dashboard
│   ├── profile.html             # User profile
│   ├── rac_logo.png             # RAC logo
│   ├── emblem.png               # Indian emblem
│   └── drdo.png                 # DRDO logo
│
├── 📁 js/                       # JavaScript
│   └── api.js                   # API client & utilities
│
├── 📁 styles/                   # CSS Stylesheets
│   └── main.css                 # Global styles
│
└── 📁 uploads/                  # Uploaded advertisement PDFs
    └── .gitkeep
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **MongoDB** - [Download MongoDB Community](https://www.mongodb.com/try/download/community) or use Docker
- **Ollama** - [Download Ollama](https://ollama.ai) (for AI scoring)
- **Git** - For version control

### Step-by-Step Setup

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/jashan-dhillon/MIRA-Matching-Interviewers-With-Resume-using-AI.git
cd MIRA-Matching-Interviewers-With-Resume-using-AI
```

#### 2️⃣ Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4️⃣ Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your values
```

Your `.env` file should contain:
```env
MONGODB_URI=mongodb://localhost:27017/
SECRET_KEY=mira_drdo_secret_key_2024

# Email (Gmail) - for sending expert invitations
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password

# AI - set to 'true' for mock scores (no Ollama needed)
USE_MOCK_LLM=false
```

> **Note:** For Gmail, you need an [App Password](https://support.google.com/accounts/answer/185833) (not your regular password).

#### 5️⃣ Start MongoDB

```bash
# Using Docker (recommended):
docker run -d -p 27017:27017 --name mira-mongo mongo:6

# Or using Homebrew (macOS):
brew services start mongodb-community

# Or using system service (Linux):
sudo systemctl start mongod
```

#### 6️⃣ Install & Start Ollama (for AI Scoring)

```bash
# Install Ollama from https://ollama.ai, then:
ollama pull llama3.2
ollama serve
```

> **Tip:** If you don't have Ollama, set `USE_MOCK_LLM=true` in `.env` to use mock scores.

#### 7️⃣ Run the Application

```bash
python app.py
```

You should see:
```
🚀 MIRA DRDO Server Starting...
   MongoDB: mongodb://localhost:27017/
   Local: http://localhost:5001
   Login: http://localhost:5001/fe/login.html

📌 First time? Call POST /api/seed to populate database
```

#### 8️⃣ Seed the Database (First Time Only)

```bash
curl -X POST http://localhost:5001/api/seed
```

This creates: 1 admin user, 17 experts, 5 advertisements, 7 items, and 8 candidates.

#### 9️⃣ Access the Application

Open: **http://localhost:5001/fe/login.html**

### Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@drdo.gov.in` | `admin123` |
| Expert | Any expert email (e.g., `nehalsingh01704@gmail.com`) | `expert123` |

---

## 🤖 AI Features

### Expert Panel Generation

The AI system scores experts for each item using a multi-factor approach:

1. **Cosine Similarity (Embeddings)** — MiniLM-L6-v2 embeddings compare expert profiles with item requirements
2. **LLM Scoring (Ollama llama3.2)** — Detailed relevance analysis with natural language reasoning
3. **Weighted Final Score** — Combined score from cosine similarity + LLM analysis

### How to Generate a Panel

1. Navigate to an **Item** page (e.g., Advt 156 → Electronics Engineering)
2. Select a **board type** from the dropdown (e.g., "Technical Screening Committee - 3 Members")
3. Click **🤖 Generate AI Panel**
4. Review AI scores and click **View AI Analysis** for detailed reasoning
5. Click **Accept All & Complete Board** to finalize

### Email & PDF Workflow

When a board is finalized:
- Each expert receives a **personalized email** with interview details
- A **formal DRDO-style PDF invitation letter** is attached with:
  - Official RAC/DRDO letterhead with logos
  - Reference number and date
  - Interview details table (venue, date, role)
  - Director's signature block

---

## 📡 API Reference

### Base URL
```
http://localhost:5001/api
```

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/captcha` | Get CAPTCHA code |
| `POST` | `/auth/signup` | Register new user |
| `POST` | `/auth/login` | Login user |
| `POST` | `/auth/logout` | Logout user |
| `GET` | `/auth/me` | Get current user |

### Advertisements
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/advertisements` | Get all advertisements |
| `GET` | `/advertisements?status=active` | Filter by status |
| `GET` | `/advertisements/<id>` | Get single advertisement |
| `GET` | `/advertisements/<id>/items` | Get items for advertisement |

### Items
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/items/<id>` | Get single item |
| `POST` | `/items/<id>/complete-board` | Finalize board & send emails |
| `GET` | `/items/<id>/panel` | Get panel for item |

### Experts
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/experts` | Get all experts |
| `GET` | `/experts?category=chairperson` | Filter by category |
| `GET` | `/experts/<id>` | Get single expert |

### AI Matching
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/matching/generate-panel/<itemId>` | Generate AI panel |
| `POST` | `/matching/calculate/<itemId>` | Calculate scores for all experts |
| `GET` | `/matching/score/<itemId>/<expertId>` | Get detailed score breakdown |
| `GET` | `/matching/ollama-status` | Check Ollama availability |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/seed` | Seed database with sample data |

---

## 👥 User Roles & Access

| Page/Feature | Admin | Expert | Candidate |
|--------------|-------|--------|-----------|
| Home Dashboard | ✅ | ✅ | ✅ |
| View Advertisements | ✅ | ✅ | ✅ |
| View Items | ✅ | ✅ | ✅ |
| Generate AI Panels | ✅ | ❌ | ❌ |
| Complete Board & Send Emails | ✅ | ❌ | ❌ |
| Experts Directory | ✅ | ✅ | ❌ |
| Admin Dashboard | ✅ | ❌ | ❌ |
| Profile | ✅ | ✅ | ✅ |

---

## 🗄 Database Schema

### Collections

#### `users`
```javascript
{
  _id: ObjectId,
  fullName: String,
  email: String (unique),
  password: String (bcrypt hashed),
  role: "admin" | "expert" | "candidate",
  createdAt: Date
}
```

#### `advertisements`
```javascript
{
  _id: ObjectId,
  advertisementNo: Number,
  title: String,
  status: "active" | "completed",
  createdAt: Date
}
```

#### `items`
```javascript
{
  _id: ObjectId,
  itemNo: Number,
  advertisementId: ObjectId,
  title: String,
  discipline: String,
  description: String,
  gateCode: String,
  vacancies: { UR, EWS, OBC, SC, ST, Total },
  boardStatus: "completed" | null
}
```

#### `experts`
```javascript
{
  _id: ObjectId,
  name: String,
  role: String,
  category: "chairperson" | "departmental" | "external",
  affiliation: String,
  specialization: String,
  relevanceScore: Number (0-100),
  reason: String (AI-generated),
  email: String
}
```

#### `panels`
```javascript
{
  _id: ObjectId,
  itemId: ObjectId,
  boardType: String,
  panelists: [{
    expertId: ObjectId,
    status: "invited" | "accepted" | "declined",
    panel_role: String,
    invitedAt: Date
  }],
  status: "draft" | "completed"
}
```

---

## 🔧 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|---------|
| "Failed to load advertisements" | MongoDB not running or DB empty | Start MongoDB + run `curl -X POST http://localhost:5001/api/seed` |
| "Invalid CAPTCHA" | CAPTCHA expired | Click refresh (⟳) next to CAPTCHA |
| "SECRET_KEY required!" | Missing `.env` | Copy `.env.example` to `.env` |
| AI panel scores all 0 | Ollama not running | Run `ollama serve` or set `USE_MOCK_LLM=true` |
| Emails not sending | Bad Gmail credentials | Use [Gmail App Password](https://support.google.com/accounts/answer/185833) in `.env` |
| Port 5001 in use | Another process on port | `kill -9 $(lsof -ti:5001)` then restart |

---

<p align="center">
  <strong>MIRA DRDO</strong> - Developed for Recruitment and Assessment Centre, DRDO
  <br>
  <em>Ministry of Defence, Government of India</em>
</p>
