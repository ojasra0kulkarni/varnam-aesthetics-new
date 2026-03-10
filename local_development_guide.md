# Local Development & Testing Guide

This guide explains how to set up, configure, and test the Varnam Aesthetics application locally.

## 1. Prerequisites
- **Python 3.9+**: Ensure Python is installed and accessible in your command prompt (`python --version`).
- **Git**: For version control (optional but recommended).
- **PostgreSQL** (Optional locally, usually recommended for parity with production. The app will default to SQLite if not provided).
- **Supabase Account**: Required for image uploads.

## 2. Setup the Environment
1. **Navigate to the project root:**
   ```bash
   cd o:\Antigravity_Projects\VarnamAsthetics
   ```
2. **Create a Virtual Environment:**
   Run the following command to create a virtual environment named `venv`.
   ```bash
   python -m venv venv
   ```
3. **Activate the Virtual Environment:**
   - On Windows:
     ```cmd
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 3. Configure Environment Variables
1. Ensure the `.env` file exists in the **root** of your project (not in the `api/` folder). If it doesn't, create it based on `.env.example`.
2. Fill in the necessary configurations:
   ```env
   # .env
   SECRET_KEY=generate_a_random_secret_string
   FLASK_APP=api/index.py
   FLASK_DEBUG=1
   
   # Optional: Local Database URI (defaults to sqlite database varna.db in the api/ folder if empty)
   # DATABASE_URI=sqlite:///varnam.db 
   
   # Supabase Setup (Required for image uploads)
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   
   # Email configuration (Required for order notifications)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   EMAIL_HOST_USER=your_gmail_address
   EMAIL_HOST_PASSWORD=your_gmail_app_password
   ```

## 4. Initializing the Database
The application automatically attempts to create the required database tables and a default admin user the first time it starts, if they don't exist.

The default admin credentials created will be:
- **Email:** `admin@varnamaesthetics.com`
- **Password:** `password`

*Note: Please change the admin password via the admin dashboard immediately after logging in for the first time.*

## 5. Running the Application
To run the server locally, execute the `index.py` file directly or use the Flask CLI.
```bash
python api/index.py
```
*Alternatively:*
```bash
flask --app api/index.py run --debug
```

## 6. Testing the Application
Once the server is running, you can test it by opening a web browser.
1. **Public Site:** Visit `http://127.0.0.1:5000/` to test the user-facing storefront.
2. **Admin Dashboard:** Visit `http://127.0.0.1:5000/admin/login` to login as an admin. Use the default credentials mentioned above.
3. **Cart & Checkout Logic:** Add products to the cart and attempt to check out. Monitor the server terminal to see email sending attempts, Supabase upload logs, or potential errors.

## Troubleshooting
- **Images not uploading:** Verify `SUPABASE_URL` and `SUPABASE_KEY` restrict your `products` and `payments` buckets, and that they are configured to be "Public".
- **Emails not sending:** Verify that `EMAIL_HOST_PASSWORD` uses an App Password (if using Gmail), rather than your standard account password.
- **SQLite errors:** Delete `api/varnam.db` to force a complete database recreation on the next start.
