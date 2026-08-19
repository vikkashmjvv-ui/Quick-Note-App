# Quick Note Application

A simple full-stack notes app built for Task 1 (Internship Task).

- **Backend:** Python (Flask) + Flask-Login for authentication
- **Database:** SQLite (`notes.db`, created automatically on first run)
- **Frontend:** Server-rendered HTML (Jinja2 templates) + CSS

## Features
- Sign Up page (Name, Email, Password) — creates one account per email
- Login page (Email + Password)
- Home page:
  - Centered "Your Notes!" title
  - Welcome message with your name
  - List of your saved notes
  - **Edit** button → makes the note title editable inline, then **Save**
  - **Delete** button → removes the note (with confirm popup)
  - Add Note box + button at the bottom to create new notes
- Logout link
- Pages are protected — visiting `/home` while logged out redirects to `/login`

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   python app.py
   ```

3. Open your browser at:
   ```
   http://127.0.0.1:5000
   ```

4. First time: click **Sign Up**, create an account with your email + password.
   Then **Login** with the same email + password.

## Project Structure
```
quick_note_app/
├── app.py                 # Flask backend (routes, auth, DB logic)
├── requirements.txt       # Python dependencies
├── notes.db                # SQLite database (auto-created on first run)
├── templates/
│   ├── base.html          # Shared layout (navbar + flash messages)
│   ├── login.html
│   ├── signup.html
│   └── home.html           # Notes list + add/edit/delete
└── static/
    └── style.css
```

## Database Tables
- **users** — id, email (unique), password (hashed), name
- **notes** — id, user_id (foreign key), title, created_at

## Notes on Security
- Passwords are hashed with Werkzeug's `generate_password_hash` — never stored in plain text.
- Each user can only see/edit/delete their own notes (enforced via `user_id` checks in every query).
