# BookShare - Library Management System with AI Recommendations

A modern library management system built with Flask, featuring AI-powered book recommendations using TF-IDF content-based filtering.

## 🎯 Features

### Core Library Management
- **Book Management**: Add, edit, search, and manage library inventory with ISBN support
- **Borrower Management**: Track library patrons and their complete loan history
- **Loan System**: Record loans, process returns, and track overdue items with status tracking
- **Advanced Search**: Fast full-text search across books (title, author, ISBN, genre) and borrowers

### AI-Powered Features ⭐
- **Content-Based Recommendations**: TF-IDF + cosine similarity for suggesting similar books
- **Book-to-Book Similarity**: "Top 3 Similar Books" on every book detail page
- **Borrower-Based Recommendations**: Personalized suggestions based on reading history
- **Real-Time Performance**: < 20ms query time with smart caching

### Automated Reminders 📧
- **Smart Notifications**: Automatic emails sent N days before due, on due date, and N days after overdue
- **APScheduler Integration**: Daily cron job (9 AM) for automated processing
- **Deduplication**: Tracks sent notifications to prevent spam
- **Manual Triggers**: Admin dashboard button + CLI command for immediate sending
- **SMTP Support**: Works with Gmail, SendGrid, Mailgun, or MailHog for testing

### User Interface
- **Responsive Design**: Clean Tailwind CSS interface that works on all devices
- **Interactive Forms**: Dynamic loan creation with search, live due date calculation
- **AJAX Recommendations**: Non-blocking asynchronous loading with similarity scores
- **Status Tracking**: Visual badges for availability, loan status, and overdue items
- **Admin Dashboard**: System statistics, cache management, manual reminder triggers

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   cd bookshare
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   flask init-db
   ```

6. **Seed with sample data (optional)**
   ```bash
   flask seed-db --books 1000 --borrowers 50 --loans 200
   ```

7. **Run the application**
   ```bash
   python run.py
   ```

   The app will be available at `http://localhost:5000`

## 📁 Project Structure

```
bookshare/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── routes/              # Blueprint routes
│   │   ├── dashboard.py
│   │   ├── books.py
│   │   ├── borrowers.py
│   │   ├── loans.py
│   │   ├── recommendations.py
│   │   └── admin.py
│   ├── services/            # Business logic (AI, email)
│   ├── templates/           # HTML templates
│   ├── static/              # CSS, JS, images
│   └── utils/               # Helper functions
├── scripts/
│   └── seed.py              # Data seeding script
├── tests/                   # Unit and functional tests
├── migrations/              # Database migrations
├── config.py                # Configuration
├── run.py                   # Entry point
└── requirements.txt         # Dependencies
```

## 🔧 Configuration

Key settings in `.env`:

- `SECRET_KEY`: Flask session secret
- `DATABASE_URL`: Database connection string
- `SMTP_*`: Email configuration for reminders
- `REMINDER_BEFORE_DUE`: Days before due date to send reminder
- `RECOMMENDATIONS_TOP_K`: Number of recommendations to show

## 🧪 Testing

Run tests with pytest:

```bash
pytest
pytest --cov=app  # With coverage
```

## 📊 CLI Commands

```bash
flask init-db              # Initialize database
flask seed-db              # Seed with sample data
flask rebuild-recs         # Rebuild recommendation cache
```

## 🤖 AI Recommendations

The system uses **TF-IDF (Term Frequency-Inverse Document Frequency)** content-based filtering to recommend similar books based on:

- Book title
- Author name
- Genre
- Description text

Recommendations are computed using cosine similarity between book feature vectors.

## 📧 Email Reminders

Automated reminders are sent:
- **3 days before** due date (configurable)
- **On** due date
- **3 days after** if overdue (configurable)

Configure SMTP settings in `.env` to enable email functionality.

## 🛠️ Development

### Database Migrations

```bash
flask db init
flask db migrate -m "Your migration message"
flask db upgrade
```

### Adding New Features

1. Create models in `app/models.py`
2. Add routes in `app/routes/`
3. Create templates in `app/templates/`
4. Add business logic in `app/services/`

## 📝 License

This project is developed as part of an FYP (Final Year Project) for academic purposes.

## 🙏 Acknowledgments

- Flask framework
- scikit-learn for ML algorithms
- Faker for synthetic data generation

---

**Note**: This is a development version. For production deployment, ensure proper security configurations, use a production-grade database (PostgreSQL/MySQL), and set up proper email credentials.
