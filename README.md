# 🎓 CET Admission System

A comprehensive web-based admission system for Karnataka Common Entrance Test (CET) engineering admissions, built with Django.

## 📋 Table of Contents
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Demo Credentials](#demo-credentials)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🎯 **Three Core Modules**
- **Student Module**: Registration, profile management, course applications, document upload
- **Institution Module**: Course management, student tracking, seat matrix monitoring
- **Admin Module**: System administration, score generation, counseling management

### 🔐 **Authentication System**
- Separate login portals for each user type
- Username/Email flexible login
- Role-based access control
- Secure session management

### 📚 **Student Features**
- ✅ Complete profile management
- ✅ Course preference selection (up to 5 choices)
- ✅ Document upload with AI verification (90% success rate)
- ✅ CET score viewing and rank tracking
- ✅ Counseling round participation
- ✅ Seat allotment and acceptance

### 🏛️ **Institution Features**
- ✅ Course and seat management
- ✅ Admitted student tracking
- ✅ Seat matrix monitoring
- ✅ Occupancy rate analytics
- ✅ Student contact information

### ⚙️ **Admin Features**
- ✅ Student application management
- ✅ CET score generation (realistic mock data)
- ✅ Counseling round execution
- ✅ Institution monitoring
- ✅ System reports and analytics

### 🤖 **Mock Features (Free for Educational Use)**
- **AI Document Verification**: Simulated with realistic confidence scores
- **Payment Gateway**: Mock payment processing
- **Email/SMS Notifications**: Simulated messaging system
- **Score Generation**: Realistic CET score and rank algorithms

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Student       │    │   Institution   │    │     Admin       │
│   Module        │    │   Module        │    │    Module       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Django Core   │
                    │   Application   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   SQLite DB     │
                    │   (Development) │
                    └─────────────────┘
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/cet-admission-system.git
cd cet-admission-system
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load demo data
python manage.py setup_demo_data
```

### Step 5: Generate CET Scores (Optional)
```bash
python manage.py generate_cet_scores --all
```

### Step 6: Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the application.

## 📖 Usage

### 🎯 **Access Points**

| User Type | Login URL | Dashboard |
|-----------|-----------|-----------|
| **Student** | `/auth/student/login/` | `/student/dashboard/` |
| **Institution** | `/auth/institution/login/` | `/institution/dashboard/` |
| **Admin** | `/auth/admin/login/` | `/admission/admin/dashboard/` |

### 🔑 **Demo Credentials**

| Role | Username | Email | Password |
|------|----------|-------|----------|
| **Student** | `student1` | `student1@example.com` | `student123` |
| **Admin** | `admin` | `admin@cet.edu` | `admin123` |
| **Institution** | `rvce_admin` | `admin@rvce.edu` | `admin123` |

### 📱 **Student Workflow**
1. **Register** → Complete profile → Upload documents
2. **Apply** → Select course preferences → Submit application
3. **Wait** → CET scores generated → Counseling begins
4. **Accept** → Seat allotment → Accept/Reject seat

### 🏛️ **Institution Workflow**
1. **Login** → View dashboard → Manage courses
2. **Monitor** → Track admissions → Check seat matrix
3. **Manage** → View student details → Contact information

### ⚙️ **Admin Workflow**
1. **Login** → System overview → Generate scores
2. **Execute** → Run counseling → Monitor applications
3. **Analyze** → View reports → System management

## 🛠️ Management Commands

```bash
# Setup demo data (institutions, courses, sample users)
python manage.py setup_demo_data

# Generate CET scores for all students
python manage.py generate_cet_scores --all

# Generate score for specific student
python manage.py generate_cet_scores --student-id CET2025000001

# Create superuser
python manage.py createsuperuser
```

## 🎨 Engineering Courses Available

- **CSE** - Computer Science Engineering
- **ISE** - Information Science Engineering  
- **ECE** - Electronics and Communication Engineering
- **EEE** - Electrical and Electronics Engineering
- **MECH** - Mechanical Engineering
- **CIVIL** - Civil Engineering
- **BIOTECH** - Biotechnology
- **CHEM** - Chemical Engineering
- **AERO** - Aeronautical Engineering
- **AUTO** - Automobile Engineering

## 🏫 Demo Institutions

- **RVCE** - RV College of Engineering
- **BMSCE** - BMS College of Engineering
- **PESU** - PES University
- **UOM** - Mysore University
- **NIET** - NIE Institute of Technology

## 📊 API Endpoints

```
GET  /api/students/          # List all students
GET  /api/institutions/      # List all institutions  
GET  /api/applications/      # List all applications
POST /api/mock-notification/ # Send mock notification
POST /api/mock-payment/      # Process mock payment
```

## 🔧 Configuration

### Environment Variables (.env)
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration
- **Development**: SQLite (default)
- **Production**: PostgreSQL (recommended)

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test student
python manage.py test authentication
python manage.py test institution
```

## 📁 Project Structure

```
cet_admission_system/
├── admission/              # Main admission logic
├── authentication/         # User authentication
├── student/               # Student module
├── institution/           # Institution module
├── api/                   # REST API endpoints
├── templates/             # HTML templates
├── static/               # CSS, JS, images
├── media/                # User uploads
├── manage.py             # Django management
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Educational Purpose

This system is designed for educational purposes and demonstrates:
- Django web development best practices
- Role-based authentication systems
- Database design and relationships
- RESTful API development
- Responsive web design
- Mock service integration

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the demo credentials above

## 🙏 Acknowledgments

- Django framework and community
- Bootstrap for responsive design
- Font Awesome for icons
- All contributors and testers

---

**⭐ If you find this project helpful, please give it a star!**

Made with ❤️ for educational purposes