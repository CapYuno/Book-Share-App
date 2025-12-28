# HTML Templates

## Base Template

### app/templates/base.html

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}BookShare{% endblock %}</title>

    <script src="https://cdn.tailwindcss.com"></script>

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

    {% block extra_head %}{% endblock %}
</head>

<body class="bg-gray-50 min-h-screen">
    <nav class="nav-modern">
        <div class="container mx-auto px-4">
            <div class="flex justify-between items-center py-4">
                <a href="/" class="nav-brand">
                    <i class="fas fa-book"></i>
                    BookShare
                </a>

                <div class="nav-links flex gap-2">
                    <a href="/" class="nav-link">
                        <i class="fas fa-chart-line"></i>
                        <span class="hidden md:inline">Dashboard</span>
                    </a>
                    <a href="/books" class="nav-link">
                        <i class="fas fa-book-open"></i>
                        <span class="hidden md:inline">Books</span>
                    </a>
                    <a href="/borrowers" class="nav-link">
                        <i class="fas fa-users"></i>
                        <span class="hidden md:inline">Borrowers</span>
                    </a>
                    <a href="/loans" class="nav-link">
                        <i class="fas fa-exchange-alt"></i>
                        <span class="hidden md:inline">Loans</span>
                    </a>
                    <a href="/admin" class="nav-link">
                        <i class="fas fa-cog"></i>
                        <span class="hidden md:inline">Admin</span>
                    </a>
                </div>

                <button class="mobile-menu-button" onclick="toggleMobileMenu()">
                    <i class="fas fa-bars"></i>
                </button>
            </div>
        </div>
    </nav>

    <div class="mobile-menu" id="mobileMenu">
        <div class="mobile-menu-header">
            <a href="/" class="nav-brand">
                <i class="fas fa-book"></i>
                BookShare
            </a>
            <button class="mobile-menu-close" onclick="toggleMobileMenu()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="mobile-menu-links">
            <a href="/" class="mobile-menu-link">
                <i class="fas fa-chart-line"></i>
                Dashboard
            </a>
            <a href="/books" class="mobile-menu-link">
                <i class="fas fa-book-open"></i>
                Books
            </a>
            <a href="/borrowers" class="mobile-menu-link">
                <i class="fas fa-users"></i>
                Borrowers
            </a>
            <a href="/loans" class="mobile-menu-link">
                <i class="fas fa-exchange-alt"></i>
                Loans
            </a>
            <a href="/admin" class="mobile-menu-link">
                <i class="fas fa-cog"></i>
                Admin
            </a>
        </div>
    </div>

    {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
    <div class="container mx-auto px-4 mt-4">
        {% for category, message in messages %}
        <div class="flash-modern 
                        {% if category == 'success' %}flash-success
                        {% elif category == 'error' %}flash-error
                        {% elif category == 'warning' %}flash-warning
                        {% else %}flash-info{% endif %}">
            <i
                class="fas fa-{% if category == 'success' %}check-circle{% elif category == 'error' %}exclamation-circle{% elif category == 'warning' %}exclamation-triangle{% else %}info-circle{% endif %}"></i>
            {{ message }}
        </div>
        {% endfor %}
    </div>
    {% endif %}
    {% endwith %}

    <main class="container mx-auto px-4 py-8">
        {% block content %}{% endblock %}
    </main>

    <footer class="footer-modern">
        <div class="container mx-auto px-4 text-center">
            <p>&copy; 2025 BookShare Library Management System - FYP Project</p>
        </div>
    </footer>

    {% block extra_js %}{% endblock %}

    <script>
        function toggleMobileMenu() {
            const menu = document.getElementById('mobileMenu');
            menu.classList.toggle('active');
        }
    </script>
</body>

</html>
```

## Dashboard Templates

### app/templates/dashboard/index.html

```html
{% extends "base.html" %}

{% block title %}Dashboard - BookShare{% endblock %}

{% block content %}
<div class="mb-8 fade-in">
    <h1 class="text-4xl font-bold text-black mb-2">Dashboard</h1>
    <p class="text-gray">Welcome to BookShare Library Management System</p>
</div>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <div class="stat-card fade-in">
        <div class="flex items-center justify-between">
            <div>
                <p class="stat-label">Total Books</p>
                <p class="stat-value">{{ total_books }}</p>
            </div>
            <div class="stat-icon">
                <i class="fas fa-book"></i>
            </div>
        </div>
    </div>

    <div class="stat-card fade-in" style="animation-delay: 0.1s;">
        <div class="flex items-center justify-between">
            <div>
                <p class="stat-label">Borrowers</p>
                <p class="stat-value">{{ total_borrowers }}</p>
            </div>
            <div class="stat-icon">
                <i class="fas fa-users"></i>
            </div>
        </div>
    </div>

    <div class="stat-card fade-in" style="animation-delay: 0.2s;">
        <div class="flex items-center justify-between">
            <div>
                <p class="stat-label">Active Loans</p>
                <p class="stat-value">{{ active_loans }}</p>
            </div>
            <div class="stat-icon">
                <i class="fas fa-bookmark"></i>
            </div>
        </div>
    </div>

    <div class="stat-card fade-in" style="animation-delay: 0.3s;">
        <div class="flex items-center justify-between">
            <div>
                <p class="stat-label">Overdue</p>
                <p class="stat-value">{{ overdue_loans }}</p>
            </div>
            <div class="stat-icon">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
        </div>
    </div>
</div>

<div class="card-modern mb-8">
    <h2 class="text-2xl font-bold text-black mb-6">Quick Actions</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <a href="/books/new" class="quick-action">
            <p class="quick-action-content">
                <i class="fas fa-plus-circle"></i>
                Add New Book
            </p>
        </a>
        <a href="/borrowers/new" class="quick-action">
            <p class="quick-action-content">
                <i class="fas fa-user-plus"></i>
                Add New Borrower
            </p>
        </a>
        <a href="/loans/new" class="quick-action">
            <p class="quick-action-content">
                <i class="fas fa-file-alt"></i>
                Create Loan
            </p>
        </a>
    </div>
</div>

<div class="ai-section">
    <h2 class="text-2xl font-bold mb-2">
        <i class="fas fa-robot"></i>
        AI-Powered Recommendations
    </h2>
    <p class="mb-4">✅ <strong>Now Live!</strong> Get personalized book recommendations powered by TF-IDF machine
        learning.</p>
    <p class="text-gray-300">Visit any book detail page to see AI-generated recommendations based on content similarity.
    </p>
    <a href="/books/" class="btn-modern btn-secondary mt-4 inline-block">
        <i class="fas fa-book-open"></i>
        Browse Books
    </a>
</div>
{% endblock %}
```

## Book Templates

Due to character limits, the complete book templates (`list.html`, `detail.html`, `form.html`) total over 500 lines of code. They include:

- **books/list.html**: Book listing with autocomplete search functionality, search history, live results dropdown
- **books/detail.html**: Book details page with AI recommendation display and dynamic JavaScript loading
- **books/form.html**: Book create/edit form with validation and AI description helper

## Borrower Templates

### app/templates/borrowers/list.html

```html
{% extends "base.html" %}

{% block title %}Borrowers - BookShare{% endblock %}

{% block content %}
<div class="mb-8">
    <div class="flex justify-between items-center">
        <div>
            <h1 class="text-4xl font-bold text-black mb-2">
                <i class="fas fa-users"></i> Borrowers
            </h1>
            <p class="text-gray">Manage library members</p>
        </div>
        <a href="/borrowers/new" class="btn-modern btn-primary">
            <i class="fas fa-user-plus"></i> Add Borrower
        </a>
    </div>
</div>

<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
    <div class="stat-card">
        <div class="flex justify-between items-start mb-4">
            <div>
                <p class="stat-label">Total Borrowers</p>
                <p class="stat-value">{{ borrowers|length }}</p>
            </div>
            <i class="fas fa-users stat-icon"></i>
        </div>
    </div>
    <div class="stat-card">
        <div class="flex justify-between items-start mb-4">
            <div>
                <p class="stat-label">Active Borrowers</p>
                <p class="stat-value">{{ borrowers|selectattr('loans')|list|length }}</p>
            </div>
            <i class="fas fa-user-check stat-icon"></i>
        </div>
    </div>
    <div class="stat-card">
        <div class="flex justify-between items-start mb-4">
            <div>
                <p class="stat-label">New This Month</p>
                <p class="stat-value">-</p>
            </div>
            <i class="fas fa-user-plus stat-icon"></i>
        </div>
    </div>
</div>

<div class="table-wrapper">
    <table class="table-modern">
        <thead>
            <tr>
                <th><i class="fas fa-user"></i> Name</th>
                <th><i class="fas fa-envelope"></i> Email</th>
                <th><i class="fas fa-phone"></i> Phone</th>
                <th><i class="fas fa-book-open"></i> Active Loans</th>
                <th><i class="fas fa-cog"></i> Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for borrower in borrowers %}
            <tr>
                <td>
                    <p class="font-semibold text-black">{{ borrower.name }}</p>
                </td>
                <td>
                    <p class="text-gray">{{ borrower.email }}</p>
                </td>
                <td>
                    <p class="text-gray">{{ borrower.phone or '-' }}</p>
                </td>
                <td>
                    {% set active_loans = borrower.loans|selectattr('returned_at', 'none')|list|length %}
                    <span class="badge-modern {{ 'badge-borrowed' if active_loans > 0 else 'badge-available' }}">
                        {{ active_loans }}
                    </span>
                </td>
                <td>
                    <div class="flex gap-2">
                        <a href="/borrowers/{{ borrower.id }}" class="text-black hover:underline font-medium">
                            <i class="fas fa-eye"></i> View
                        </a>
                        <span class="text-gray">|</span>
                        <a href="/borrowers/{{ borrower.id }}/edit" class="text-black hover:underline font-medium">
                            <i class="fas fa-edit"></i> Edit
                        </a>
                    </div>
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="5" class="px-6 py-12 text-center">
                    <p class="text-gray text-lg mb-4">No borrowers found</p>
                    <a href="/borrowers/new" class="text-black hover:underline font-semibold">
                        <i class="fas fa-user-plus"></i> Add your first borrower
                    </a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

### app/templates/borrowers/form.html

```html
{% extends "base.html" %}

{% block title %}{{ 'Edit' if borrower else 'Add' }} Borrower - BookShare{% endblock %}

{% block content %}
<div class="mb-4">
    <a href="{{ '/borrowers/' + borrower.id|string if borrower else '/borrowers' }}"
        class="text-black hover:underline font-semibold">
        ← Back to {{ 'Borrower' if borrower else 'Borrowers' }}
    </a>
</div>

<div class="bg-white rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
    <h1 class="text-3xl font-bold text-gray-800 mb-6">
        {{ '✏️ Edit Borrower' if borrower else '👤 Add New Borrower' }}
    </h1>

    <form method="post" class="space-y-6">
        <div>
            <label for="name" class="block text-sm font-semibold text-gray-700 mb-2">
                Full Name <span class="text-red-500">*</span>
            </label>
            <input type="text" id="name" name="name" value="{{ borrower.name if borrower else '' }}" required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent"
                placeholder="Enter full name">
        </div>

        <div>
            <label for="email" class="block text-sm font-semibold text-gray-700 mb-2">
                Email Address <span class="text-red-500">*</span>
            </label>
            <input type="email" id="email" name="email" value="{{ borrower.email if borrower else '' }}" required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent"
                placeholder="borrower@example.com">
            <p class="text-sm text-gray-500 mt-1">Used for loan reminders</p>
        </div>

        <div>
            <label for="phone" class="block text-sm font-semibold text-gray-700 mb-2">
                Phone Number
            </label>
            <input type="tel" id="phone" name="phone" value="{{ borrower.phone if borrower else '' }}"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent"
                placeholder="+1 (555) 123-4567 (optional)">
        </div>

        <div class="flex gap-4 pt-4">
            <button type="submit"
                class="flex-1 bg-black text-white px-6 py-3 rounded-lg hover:bg-gray-800 transition font-semibold">
                {{ '💾 Save Changes' if borrower else '👤 Add Borrower' }}
            </button>
            <a href="{{ '/borrowers/' + borrower.id|string if borrower else '/borrowers' }}"
                class="flex-1 text-center bg-white text-black border-2 border-black px-6 py-3 rounded-lg hover:bg-black hover:text-white transition font-semibold">
                Cancel
            </a>
        </div>
    </form>
</div>
{% endblock %}
```

## Loan Templates

Due to character limits, the complete loan templates include:

- **loans/list.html**: Loan listing table with filters (active, overdue, returned) and status indicators
- **loans/form.html**: Interactive loan creation form with book/borrower search and selection interface

## Admin Template

The admin dashboard template includes system statistics, AI recommendation management, email reminder controls, and data import/export functionality.

Note: For the complete HTML code of all templates including the detailed implementations of `books/list.html`, `books/detail.html`, `books/form.html`, `borrowers/detail.html`, `loans/list.html`, `loans/form.html`, and `admin/dashboard.html`, please refer to the source files in `app/templates/` directory. These templates total over 1500 lines of HTML/Jinja2 code with extensive JavaScript for interactive features.
