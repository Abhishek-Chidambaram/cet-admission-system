# 🎓 CET Admission System

A comprehensive, bug-free web-based admission system for Karnataka Common Entrance Test (CET) engineering admissions, built with Django. This system replicates the real CET admission process with three dedicated modules and intelligent workflows.

## Table of Contents
- [Features](#features)
- [System Architecture](#system-architecture)
- [Recent Updates](#recent-updates)
- [Installation](#installation)
- [Usage](#usage)
- [Demo Credentials](#demo-credentials)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## Features

### **Three Core Modules**
- **Student Module**: Complete admission journey from registration to seat acceptance
- **Institution Module**: Course management, student tracking, and seat matrix monitoring
- **Admin Module**: System administration, score generation, and counseling management

###  **Advanced Authentication System**
- **Separate Login Portals**: Dedicated login pages for each user type
- **Flexible Login**: Username OR Email authentication
- **Role-Based Access**: Secure access control with proper error handling
- **Session Management**: Secure user sessions with automatic redirects

###  **Student Features**
- **Progressive Profile Creation**: Optional fields for gradual completion
- **Smart Course Selection**: Up to 5 preferences with institution details
- **Real-time CET Scores**: Rank tracking with category-wise rankings
- **Intelligent Counseling**: Preference-based seat allocation
- **Seat Management**: Accept/reject allotted seats with status tracking

### **Institution Features**
- **Course Portfolio Management**: Complete course and seat management
- **Student Analytics**: Admitted student tracking with contact details
- **Dynamic Seat Matrix**: Real-time occupancy monitoring
- **Performance Metrics**: Occupancy rates and admission statistics
- **Communication Hub**: Direct access to student information

###  **Admin Features**
- **System Dashboard**: Comprehensive overview with key metrics
- **Score Generation Engine**: Realistic CET score and rank algorithms
- **Counseling Automation**: Intelligent seat allocation based on preferences
- **Institution Monitoring**: Complete oversight of participating institutions
- **Advanced Analytics**: Detailed reports and system insights


##  System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Student       │    │   Institution   │    │     Admin       │
│   Portal        │    │   Portal        │    │    Portal       │
│                 │    │                 │    │                 │
│ • Profile Mgmt  │    │ • Course Mgmt   │    │ • Score Gen     │
│ • Applications  │    │ • Student Track │    │ • Counseling    │
│ • Documents     │    │ • Seat Matrix   │    │ • Analytics     │
│ • Counseling    │    │ • Analytics     │    │ • Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Django Core   │
                    │   Application   │
                    │                 │
                    │ • Authentication│
                    │ • API Layer     │
                    │ • Business Logic│
                    │ • Workflow Mgmt │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │   Layer         │
                    │                 │
                    │ • SQLite (Dev)  │
                    │ • PostgreSQL    │
                    │ • File Storage  │
                    └─────────────────┘
```

##  Recent Updates

###  **Major Bug Fixes (Latest Release)**
- **Profile Creation**: Fixed required field issues - all fields now optional for gradual completion
- **Application Workflow**: Automated verification process when documents are approved
- **Document Management**: Prevented duplicate uploads with clear error messages
- **Counseling Logic**: Implemented preference-based seat allocation algorithm
- **Access Control**: Enhanced security with proper error handling and redirects
- **Data Integrity**: Fixed category rank generation and score calculations
- **User Experience**: Smooth workflows with intelligent error recovery

###  **System Improvements**
- **Database Migration**: Seamless field updates without data loss
- **Form Validation**: Enhanced validation with user-friendly error messages
- **Workflow Automation**: Automatic status updates throughout the admission process
- **Testing Framework**: Comprehensive system testing with automated verification

##  Installation

### Prerequisites
- Python 3.8+ (Recommended: Python 3.10+)
- pip (Python package manager)
- Git
- Virtual environment support

### Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/cet-admission-system.git
cd cet-admission-system

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Database setup
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Load demo data (institutions, courses, sample users)
python manage.py setup_demo_data

# Generate sample CET scores
python manage.py generate_cet_scores --all

# Test the system
python manage.py test_system

# Start development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the application.

##  Usage

###  **Access Points & Login Portals**

| User Type | Login URL | Dashboard | Features |
|-----------|-----------|-----------|----------|
| **Student** | `/auth/student/login/` | `/student/dashboard/` | Profile, Applications, Documents, Scores |
| **Institution** | `/auth/institution/login/` | `/institution/dashboard/` | Courses, Students, Seat Matrix |
| **Admin** | `/auth/admin/login/` | `/admission/admin/dashboard/` | System Management, Counseling |
| **All Options** | `/auth/login/` | - | Unified login selection page |

###  **Demo Credentials (Username OR Email)**

| Role | Username | Email | Password | Access Level |
|------|----------|-------|----------|--------------|
| **Student** | `student1` | `student1@example.com` | `student123` | Student Portal |
| **Admin** | `admin` | `admin@kcet.edu` | `abhi@123` | Full System Access |
| **Institution** | `rvce_admin` | `admin@rvce.edu` | `admin123` | RVCE Management |
| **Institution** | `bmsce_admin` | `admin@bmsce.edu` | `admin123` | BMSCE Management |
| **Institution** | `pesu_admin` | `admin@pesu.edu` | `admin123` | PESU Management |

###  **Complete Student Journey**
1. **Registration** → Create account with email/phone verification
2. **Profile Setup** → Complete personal, academic, and family details
3. **Document Upload** → Upload and verify required certificates
4. **Course Application** → Select up to 5 course preferences
5. **CET Scores** → View generated scores and rankings
6. **Counseling** → Participate in automated seat allocation
7. **Seat Acceptance** → Accept or reject allotted seats

###  **Institution Management Workflow**
1. **Dashboard Overview** → Monitor admissions and occupancy
2. **Course Management** → View offered courses and seat distribution
3. **Student Tracking** → Access admitted student details
4. **Seat Matrix Analysis** → Real-time seat availability monitoring
5. **Communication** → Direct access to student contact information

###  **Admin Control Panel**
1. **System Monitoring** → Overview of all applications and institutions
2. **Score Generation** → Create realistic CET scores for students
3. **Counseling Execution** → Run automated seat allocation rounds
4. **Analytics & Reports** → Comprehensive system insights
5. **User Management** → Monitor and manage all system users

##  Management Commands

```bash
# System Setup
python manage.py setup_demo_data              # Create institutions, courses, sample users
python manage.py createsuperuser              # Create admin user

# CET Score Management
python manage.py generate_cet_scores --all    # Generate scores for all students
python manage.py generate_cet_scores --student-id CET2025000001  # Specific student

# System Testing & Verification
python manage.py test_system                   # Comprehensive system test
python manage.py test                          # Run Django unit tests
python manage.py test student                  # Test specific app

# Database Management
python manage.py makemigrations                # Create new migrations
python manage.py migrate                       # Apply migrations
python manage.py showmigrations                # Show migration status
```

##  Available Engineering Courses

### **Core Engineering Disciplines**
- **CSE** - Computer Science Engineering
- **ISE** - Information Science Engineering  
- **ECE** - Electronics and Communication Engineering
- **EEE** - Electrical and Electronics Engineering
- **MECH** - Mechanical Engineering
- **CIVIL** - Civil Engineering

### **Specialized Engineering Fields**
- **BIOTECH** - Biotechnology Engineering
- **CHEM** - Chemical Engineering
- **AERO** - Aeronautical Engineering
- **AUTO** - Automobile Engineering

##  Participating Demo Institutions

| Code | Institution Name | Type | Location | Courses |
|------|------------------|------|----------|---------|
| **RVCE** | RV College of Engineering | Private | Bangalore | All 10 Courses |
| **BMSCE** | BMS College of Engineering | Private | Bangalore | All 10 Courses |
| **PESU** | PES University | Private | Bangalore | All 10 Courses |
| **UOM** | University of Mysore | Government | Mysore | All 10 Courses |
| **NIET** | NIE Institute of Technology | Government | Mysore | All 10 Courses |

##  Testing

### **Automated System Testing**
```bash
# Complete system functionality test
python manage.py test_system

# Expected Output:
#  Testing CET Admission System...
#  Student profile creation test passed
# Application process test passed  
#  Document verification test passed
#  CET score generation test passed
#  Counseling process test passed
#  All tests completed successfully!
```

### **Unit Testing**
```bash
# Run all Django tests
python manage.py test

# Test specific modules
python manage.py test student.tests
python manage.py test authentication.tests
python manage.py test institution.tests
python manage.py test admission.tests
```

### **Manual Testing Checklist**
- [ ] User registration and login (all three portals)
- [ ] Student profile creation and editing
- [ ] Document upload and AI verification
- [ ] Course application and preference selection
- [ ] CET score viewing and rank display
- [ ] Counseling participation and seat allocation
- [ ] Institution dashboard and student management
- [ ] Admin score generation and counseling execution

##  API Documentation

### **REST API Endpoints**
```
# Student Management
GET  /api/students/                    # List all students
GET  /api/students/{id}/               # Get specific student
POST /api/students/                    # Create student (admin only)

# Institution Management  
GET  /api/institutions/                # List all institutions
GET  /api/institutions/{id}/           # Get specific institution
GET  /api/institutions/{id}/courses/   # Get institution courses

# Application Management
GET  /api/applications/                # List all applications
GET  /api/applications/{id}/           # Get specific application
PUT  /api/applications/{id}/           # Update application status

# Mock Services
POST /api/mock-notification/           # Send mock notification
POST /api/mock-payment/                # Process mock payment
GET  /api/system-stats/                # Get system statistics
```

### **API Authentication**
```python
# Token-based authentication
headers = {
    'Authorization': 'Token your-api-token-here',
    'Content-Type': 'application/json'
}
```

## 🔧 Configuration

### **Environment Variables (.env)**
```env
# Core Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database Configuration
DB_NAME=cet_admission_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# File Upload Settings
MAX_UPLOAD_SIZE=5242880  # 5MB
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png

# CET Specific Settings
CET_EXAM_YEAR=2024
MOCK_AI_SUCCESS_RATE=0.9
```

### **Production Deployment**
```bash
# Install production dependencies
pip install gunicorn psycopg2-binary

# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn cet_admission_system.wsgi:application
```

##  Detailed Project Structure

```
cet_admission_system/
├── 📁 admission/                    # Core admission logic
│   ├── models.py                   # CET exam, centers, mock data
│   ├── views.py                    # Admin dashboard, counseling
│   └── management/commands/        # Admin management commands
├── 📁 authentication/              # User authentication system
│   ├── models.py                   # Custom user model
│   ├── views.py                    # Login portals (3 separate)
│   ├── forms.py                    # Custom auth forms
│   └── templates/                  # Login page templates
├── 📁 student/                     # Student module
│   ├── models.py                   # Profile, application, documents
│   ├── views.py                    # Student workflows
│   ├── forms.py                    # Student forms
│   ├── management/commands/        # Score generation, testing
│   └── templates/                  # Student interface templates
├── 📁 institution/                 # Institution module
│   ├── models.py                   # Institution, courses, seat matrix
│   ├── views.py                    # Institution dashboard
│   └── templates/                  # Institution interface
├── 📁 api/                         # REST API layer
│   ├── views.py                    # API endpoints
│   ├── serializers.py              # Data serialization
│   └── urls.py                     # API routing
├── 📁 templates/                   # Global templates
│   ├── base.html                   # Base template
│   ├── 📁 admission/               # Admin templates
│   ├── 📁 authentication/          # Auth templates
│   ├── 📁 student/                 # Student templates
│   └── 📁 institution/             # Institution templates
├── 📁 static/                      # Static assets
│   ├── 📁 css/                     # Stylesheets
│   ├── 📁 js/                      # JavaScript files
│   └── 📁 images/                  # Image assets
├── 📁 media/                       # User uploads
│   ├── 📁 student_photos/          # Profile photos
│   └── 📁 student_documents/       # Uploaded documents
├── 📄 manage.py                    # Django management script
├── 📄 requirements.txt             # Python dependencies
├── 📄 README.md                    # This documentation
├── 📄 LICENSE                      # MIT License
└── 📄 .gitignore                   # Git ignore rules
```

## Contributing

We welcome contributions! Here's how to get started:

### **Development Setup**
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/cet-admission-system.git
cd cet-admission-system

# Create feature branch
git checkout -b feature/amazing-feature

# Make your changes and test
python manage.py test_system

# Commit and push
git commit -m 'Add amazing feature'
git push origin feature/amazing-feature

# Create Pull Request
```

### **Contribution Guidelines**
- Follow Django best practices
- Write comprehensive tests for new features
- Update documentation for any API changes
- Ensure all tests pass before submitting PR
- Use meaningful commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Educational Value

This system demonstrates advanced concepts in:

### **Web Development**
- Django framework mastery
- RESTful API design
- Database modeling and relationships
- User authentication and authorization
- File upload and management

### **Software Engineering**
- Clean code architecture
- Test-driven development
- Error handling and validation
- Workflow automation
- System integration

### **UI/UX Design**
- Responsive web design
- User experience optimization
- Accessibility compliance
- Progressive enhancement
- Cross-browser compatibility

## Performance & Scalability

- **Database Optimization**: Efficient queries with select_related and prefetch_related
- **Caching Strategy**: Built-in Django caching for improved performance
- **File Management**: Organized media handling with size restrictions
- **API Rate Limiting**: Token-based authentication with proper throttling
- **Scalable Architecture**: Modular design supporting horizontal scaling

## Support & Community

### **Getting Help**
-  **Issues**: Create detailed GitHub issues for bugs or feature requests
-  **Documentation**: Comprehensive inline documentation and comments
-  **Testing**: Use `python manage.py test_system` to verify functionality
-  **Discussions**: GitHub Discussions for questions and ideas

### **Quick Troubleshooting**
```bash
# Common issues and solutions
python manage.py test_system          # Verify system functionality
python manage.py migrate              # Apply pending migrations
python manage.py collectstatic        # Fix static file issues
python manage.py setup_demo_data      # Reset demo data
```

##  Acknowledgments

- **Django Community**: For the robust web framework
- **Bootstrap Team**: For responsive UI components
- **Font Awesome**: For comprehensive icon library
- **Karnataka CET Board**: For inspiration and process understanding
- **Educational Institutions**: For feedback and testing support

---

**⭐ If this project helps you learn or build something amazing, please give it a star!**
