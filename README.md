# Grocery Bud - Django CRUD App

A clean, minimal grocery list app built with Django featuring full CRUD functionality.

## Features
- Add grocery items
- Mark items as completed (toggle)
- Edit item names inline
- Delete items with confirmation
- Toast notifications for all actions
- Responsive, animated UI

## Setup & Run

```bash
# 1. Create & activate virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install django

# 3. Apply migrations
python manage.py migrate

# 4. (Optional) Create admin user
python manage.py createsuperuser

# 5. Run the development server
python manage.py runserver
```

Then open http://127.0.0.1:8000/ in your browser.

## Project Structure
```
CRUD_DJANGO/
├── config/               # Project settings & URLs
│   ├── settings.py
│   └── urls.py
├── grocery/              # Main app
│   ├── migrations/
│   ├── static/grocery/
│   │   └── css/          # All stylesheets
│   ├── templates/grocery/
│   │   └── index.html    # Single-page UI
│   ├── admin.py          # Admin registration
│   ├── models.py         # GroceryItem model
│   ├── urls.py           # App URL patterns
│   └── views.py          # CRUD views
└── manage.py
```

## URLs
| URL | Name | Action |
|-----|------|--------|
| `/` | `grocery:index` | List all items |
| `/add/` | `grocery:add` | Add new item (POST) |
| `/edit/<id>/` | `grocery:edit` | Redirect to edit mode |
| `/update/<id>/` | `grocery:update` | Save edited item (POST) |
| `/toggle/<id>/` | `grocery:toggle` | Toggle completed (POST) |
| `/delete/<id>/` | `grocery:delete` | Delete item (POST) |
