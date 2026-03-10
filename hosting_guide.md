# Hosting & Deployment Guide

This guide explains how to deploy the Varnam Aesthetics application, which is built as a Flask serverless application designed for Vercel, using PostgreSQL and Supabase.

## Architecture Overview
- **Frontend & Backend**: Flask application hosted as Serverless Functions on Vercel.
- **Database**: PostgreSQL database. (Can be hosted on Supabase, Heroku, Render, etc.)
- **Storage**: Supabase Storage for product images and payment screenshots.

## 1. Setting up the Database (PostgreSQL via Supabase)
1. Go to [Supabase](https://supabase.com/).
2. Create a new project.
3. Once the project is created, navigate to **Project Settings -> Database** and copy the **Connection string** (URI).
4. Save this URI; you will need it for the `DATABASE_URI` environment variable later. Don't forget to replace `[YOUR-PASSWORD]` with your actual database password in the URI if necessary.

## 2. Setting up Supabase Storage
1. In your Supabase dashboard, navigate to **Storage**.
2. Create two new buckets:
   - `products` (for product and custom request images)
   - `payments` (for payment screenshots)
3. Ensure both buckets are set to **Public**.

## 3. Deployment with Vercel

### Step 3.1: Vercel CLI (Recommended)
1. Install the Vercel CLI globally using npm:
   ```bash
   npm i -g vercel
   ```
2. Open your terminal in the project root directory.
3. Run the following command and follow the prompts to log in and link your project:
   ```bash
   vercel
   ```
   *Accept the default configuration options it provides for linking the project.*

### Step 3.2: Configure Environment Variables on Vercel
Before deploying to production, you must set the environment variables in your Vercel project settings.
1. Go to the [Vercel Dashboard](https://vercel.com/dashboard).
2. Select your newly linked project -> **Settings** -> **Environment Variables**.
3. Add the following variables:
   - `SECRET_KEY`: A strong, random string.
   - `DATABASE_URI`: Your PostgreSQL connection string (from Step 1).
   - `SUPABASE_URL`: From Supabase (Project Settings -> API -> Project URL).
   - `SUPABASE_KEY`: From Supabase (Project Settings -> API -> Project API keys -> `anon` `public`).
   - `SMTP_SERVER`: (e.g., `smtp.gmail.com`)
   - `SMTP_PORT`: (e.g., `587`)
   - `EMAIL_HOST_USER`: Your email address for sending notifications.
   - `EMAIL_HOST_PASSWORD`: Your email App Password.

### Step 3.3: First Production Deployment
1. Once environment variables are set, deploy to production:
   ```bash
   vercel --prod
   ```
2. Vercel will build the `api/index.py` according to the provided `vercel.json` file configuration, setting it up as a serverless function.
3. The application will automatically create the database tables and a default admin user (`admin@varnamaesthetics.com` / `password`) if they don't already exist on the first request.

## Post-Deployment Checklist
- Access your Vercel project URL.
- Test uploading an image to ensure Supabase integration is correct.
- Log into the admin portal (`/admin/login`) and change the default admin password immediately.
