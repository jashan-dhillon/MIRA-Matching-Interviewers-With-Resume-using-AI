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
2. [Current Status](#-current-status)
3. [Technology Stack](#-technology-stack)
4. [Project Structure](#-project-structure)
5. [Getting Started](#-getting-started)
6. [API Reference](#-api-reference)
7. [User Roles & Access](#-user-roles--access)
8. [Database Schema](#-database-schema)
9. [Frontend Pages](#-frontend-pages)
10. [Troubleshooting](#-troubleshooting)
11. [Development Guidelines](#-development-guidelines)

---

## 🎯 Project Overview

**MIRA (Manpower Intelligence & Recruitment Automation)** is a web-based recruitment and assessment management system designed for DRDO's Recruitment and Assessment Centre (RAC). The system streamlines the process of:

- **Managing recruitment advertisements** - Create, update, and track job advertisements
- **Expert panel formation** - Automatically recommend and manually select expert panelists
- **Interview board generation** - Create interview panels for various recruitment items
- **User authentication & authorization** - Role-based access for admins, experts, and candidates

### Key Features

| Feature | Description |
|---------|-------------|
| **Advertisement Management** | Create and manage recruitment advertisements with multiple items |
| **Expert Database** | Maintain a database of experts with relevance scores |
| **AI-Powered Recommendations** | Auto-suggest experts based on relevance scores |
| **Panel Generation** | Create interview panels with chairperson, departmental, and external experts |
| **Role-Based Access Control** | Different access levels for Admin, Expert, and Candidate roles |
| **Secure Authentication** | CAPTCHA-protected login and signup with bcrypt password hashing |

---

## 📊 Current Status

### ✅ Completed Features

| Module | Status | Notes |
|--------|--------|-------|
| User Authentication | ✅ Complete | Login, Signup, Logout with CAPTCHA |
| Admin Dashboard | ✅ Complete | Full CRUD operations |
| Advertisement Management | ✅ Complete | Create, Read, Update, Delete |
| Item Management | ✅ Complete | Items linked to advertisements |
| Expert Database | ✅ Complete | With relevance scoring |
| Panel Creation | ✅ Complete | Manual & automated selection |
| Role-Based Navigation | ✅ Complete | Dynamic navbar based on role |

### 🚧 Current Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │◄───►│   Flask API     │◄───►│   MongoDB       │
│   (HTML/CSS/JS) │     │   (Python)      │     │   Database      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │
        └───────────────────────┘
              localhost:5000
```

---

## 🛠 Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.x | Backend runtime |
| Flask | 3.0.0 | Web framework |
| PyMongo | 4.6.1 | MongoDB driver |
| Flask-CORS | 4.0.0 | Cross-Origin Resource Sharing |
| bcrypt | 4.1.2 | Password hashing |
| python-dotenv | 1.0.0 | Environment variables |

### Frontend
| Technology | Purpose |
|------------|---------|
| HTML5 | Page structure |
| CSS3 | Styling (custom + Poppins font) |
| Vanilla JavaScript | Client-side logic |
| Font Awesome 6.5.1 | Icons |

### Database
| Technology | Purpose |
|------------|---------|
| MongoDB | NoSQL document database |

---

## 📁 Project Structure

```
MIRA_23jan/
├── 📄 app.py                    # Main Flask application entry point
├── 📄 requirements.txt          # Python dependencies
├── 📄 .env                      # Environment variables (DO NOT COMMIT)
├── 📄 README.md                 # This documentation
│
├── 📁 routes/                   # Backend - API Route Blueprints
│   ├── __init__.py
│   ├── auth_routes.py           # Authentication endpoints
│   ├── admin_routes.py          # Admin & seed endpoints
│   ├── advertisement_routes.py  # Advertisement CRUD
│   ├── item_routes.py           # Item CRUD
│   ├── expert_routes.py         # Expert CRUD
│   └── panel_routes.py          # Panel management
│
├── 📁 fe/                       # Frontend - HTML Pages
│   ├── login.html               # Login/Signup page
│   ├── home.html                # Dashboard homepage
│   ├── admin.html               # Admin dashboard
│   ├── advertisment.html        # Advertisement details
│   ├── item.html                # Item/Board generation page
│   ├── experts.html             # Experts directory
│   ├── profile.html             # User profile
│   └── [images]                 # Logo and emblem files
│
├── 📁 js/                       # JavaScript
│   └── api.js                   # API client & utilities
│
├── 📁 styles/                   # CSS Stylesheets
│   └── main.css                 # Global styles
│
└── 📁 ai/                       # [Future] AI Modules
    └── (recommendation engine, etc.)
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **MongoDB** - [Download MongoDB Community](https://www.mongodb.com/try/download/community)
- **Git** (optional) - For version control

### Step-by-Step Setup

#### 1️⃣ Clone/Download the Project

```bash
# If using Git
git clone <repository-url>
cd MIRA_23jan

# Or simply extract the folder to your desired location
```

#### 2️⃣ Set Up Python Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

#### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4️⃣ Configure Environment Variables

The `.env` file should be present with the following variables:

```env
MONGODB_URI=mongodb://localhost:27017/
SECRET_KEY=mira_drdo_secret_key_2024
```

⚠️ **Important:** For production, change `SECRET_KEY` to a strong, unique value!

#### 5️⃣ Start MongoDB

```bash
# On Windows (if MongoDB is installed as a service, it starts automatically)
# Otherwise, run:
mongod

# On macOS/Linux:
sudo systemctl start mongod
# or
brew services start mongodb-community
```

#### 6️⃣ Run the Application

```bash
python app.py
```

You should see:
```
🚀 MIRA DRDO Server Starting...
   MongoDB: mongodb://localhost:27017/
   Local: http://localhost:5000
   Login: http://localhost:5000/MIRA_9jan/login.html

📌 First time? Call POST /api/seed to populate database
```

#### 7️⃣ Seed the Database (First Time Only)

Open the application in your browser and click the **"Seed Database"** button at the bottom-left of the login page.

Alternatively, use the API:
```bash
curl -X POST http://localhost:5000/api/seed
```

#### 8️⃣ Access the Application

- **Direct Login Page:** http://localhost:5000/fe/login.html
- **Alternative:** http://localhost:5000

### Default Login Credentials (After Seeding)

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@drdo.gov.in` | `admin123` |

---

## 📡 API Reference

### Base URL
```
http://localhost:5000/api
```

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/captcha` | Get CAPTCHA code |
| `POST` | `/auth/signup` | Register new user |
| `POST` | `/auth/login` | Login user |
| `POST` | `/auth/logout` | Logout user |
| `GET` | `/auth/me` | Get current user |

### Advertisement Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/advertisements` | Get all advertisements |
| `GET` | `/advertisements?status=active` | Get by status |
| `GET` | `/advertisements/<id>` | Get single advertisement |
| `POST` | `/advertisements` | Create advertisement |
| `PUT` | `/advertisements/<id>` | Update advertisement |
| `DELETE` | `/advertisements/<id>` | Delete advertisement |
| `GET` | `/advertisements/<id>/items` | Get items for advertisement |

### Item Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/items/<id>` | Get single item |
| `POST` | `/items` | Create item |
| `PUT` | `/items/<id>` | Update item |
| `DELETE` | `/items/<id>` | Delete item |

### Expert Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/experts` | Get all experts |
| `GET` | `/experts?category=chairperson` | Filter by category |
| `GET` | `/experts/<id>` | Get single expert |
| `POST` | `/experts` | Create expert |
| `PUT` | `/experts/<id>` | Update expert |
| `DELETE` | `/experts/<id>` | Delete expert |

### Panel Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/panels` | Get all panels |
| `GET` | `/panels/<id>` | Get single panel |
| `POST` | `/panels` | Create panel |
| `PUT` | `/panels/<id>/invite` | Update panelist status |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users` | Get all users |
| `POST` | `/seed` | Seed database with sample data |

---

## 👥 User Roles & Access

### Role Permissions Matrix

| Page/Feature | Admin | Expert | Candidate |
|--------------|-------|--------|-----------|
| Home Dashboard | ✅ | ✅ | ✅ |
| View Advertisements | ✅ | ✅ | ✅ |
| View Items | ✅ | ✅ | ✅ |
| Experts Directory | ✅ | ✅ | ❌ |
| Admin Dashboard | ✅ | ❌ | ❌ |
| Create/Edit Data | ✅ | ❌ | ❌ |
| Generate Panels | ✅ | ❌ | ❌ |
| Profile | ✅ | ✅ | ✅ |

### Role Descriptions

- **Admin:** Full access to all features, can manage advertisements, items, experts, and panels
- **Expert:** Can view advertisements, items, and expert directory; may participate in panels
- **Candidate:** Basic access to view advertisements and profile management

---

## 🗄 Database Schema

### Collections

#### `users`
```javascript
{
  _id: ObjectId,
  fullName: String,
  email: String (unique),
  password: String (hashed),
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
  createdAt: Date,
  closingDate: Date (optional)
}
```

#### `items`
```javascript
{
  _id: ObjectId,
  itemNo: Number,
  advertisementId: ObjectId (ref: advertisements),
  title: String,
  description: String,
  documentUrl: String,
  requiredBoardSize: Number (default: 5),
  createdAt: Date
}
```

#### `experts`
```javascript
{
  _id: ObjectId,
  name: String,
  role: String,
  category: "chairperson" | "departmental" | "external",
  affiliation: String (for external experts),
  relevanceScore: Number (0-100),
  reason: String,
  email: String,
  createdAt: Date
}
```

#### `panels`
```javascript
{
  _id: ObjectId,
  itemId: ObjectId (ref: items),
  boardType: String,
  panelists: [{
    expertId: ObjectId (ref: experts),
    status: "pending" | "accepted" | "declined",
    invitedAt: Date,
    respondedAt: Date
  }],
  createdAt: Date,
  status: "draft" | "confirmed"
}
```

---

## 🖥 Frontend Pages

### Page Navigation Flow

```
login.html ──► home.html ──┬──► advertisment.html ──► item.html
                           ├──► experts.html
                           ├──► admin.html
                           └──► profile.html
```

### Page Descriptions

| Page | URL | Description |
|------|-----|-------------|
| Login | `/fe/login.html` | User authentication with CAPTCHA |
| Home | `/fe/home.html` | Dashboard with active/completed advertisements |
| Advertisement | `/fe/advertisment.html?id=<id>` | View items under an advertisement |
| Item | `/fe/item.html?id=<id>` | Generate/view interview panel |
| Experts | `/fe/experts.html` | Browse expert directory |
| Admin | `/fe/admin.html` | Admin dashboard for data management |
| Profile | `/fe/profile.html` | User profile page |

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Failed to load advertisements" on Home page

**Cause:** MongoDB is not running or database is empty.

**Solution:**
```bash
# 1. Ensure MongoDB is running
mongod

# 2. Seed the database
curl -X POST http://localhost:5000/api/seed
# Or click "Seed Database" button on login page
```

#### 2. "Invalid CAPTCHA" error

**Cause:** CAPTCHA expired or server restarted.

**Solution:**
- Click the refresh button (⟳) next to the CAPTCHA
- Try logging in again

#### 3. "SECRET_KEY environment variable is required!"

**Cause:** Missing `.env` file or `SECRET_KEY` variable.

**Solution:**
Create/update `.env` file:
```env
MONGODB_URI=mongodb://localhost:27017/
SECRET_KEY=your_secret_key_here
```

#### 4. CORS errors in browser console

**Cause:** Frontend and backend on different origins.

**Solution:**
- Access application through `http://localhost:5000` (not via file://)
- CORS is already configured in the backend

#### 5. Port 5000 already in use

**Cause:** Another application is using port 5000.

**Solution:**
```bash
# Find and kill the process (Windows)
netstat -ano | findstr :5000
taskkill /PID <pid> /F

# Or change the port in app.py
app.run(debug=True, port=5001)
```

---

## 📝 Development Guidelines

### Code Style

- **Python:** Follow PEP 8 guidelines
- **JavaScript:** Use ES6+ features, camelCase for variables
- **CSS:** Use CSS variables defined in `main.css`
- **HTML:** Semantic HTML5 elements

### Adding New API Endpoints

1. Create a new route file in `/be/` directory:
   ```python
   # be/new_routes.py
   from flask import Blueprint, request, jsonify
   
   new_bp = Blueprint('new', __name__, url_prefix='/api/new')
   
   @new_bp.route('', methods=['GET'])
   def get_data():
       return jsonify({'message': 'Hello!'})
   ```

2. Register in `app.py`:
   ```python
   from routes.new_routes import new_bp
   app.register_blueprint(new_bp)
   ```

### Adding New Frontend Pages

1. Create HTML file in `/fe/` directory
2. Include required CSS and JS:
   ```html
   <link rel="stylesheet" href="../styles/main.css">
   <script src="../js/api.js"></script>
   ```
3. Add authentication check:
   ```javascript
   if (!requireAuth()) { }
   ```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes, then commit
git add .
git commit -m "Add: New feature description"

# Push and create PR
git push origin feature/new-feature
```

---

## 📞 Support & Contact

For any issues or questions regarding this project, please contact the development team.

---

<p align="center">
  <strong>MIRA DRDO</strong> - Developed for Recruitment and Assessment Centre, DRDO
  <br>
  <em>Ministry of Defence, Government of India</em>
</p>
