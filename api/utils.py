import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import threading

def send_async_email(app, msg):
    with app.app_context():
        try:
            server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Error sending email: {e}")

def send_email(subject, recipient, body):
    app = current_app._get_current_object()
    msg = MIMEMultipart()
    msg['From'] = app.config['MAIL_USERNAME']
    msg['To'] = recipient
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    thr = threading.Thread(target=send_async_email, args=[app, msg])
    thr.start()

import os
import uuid
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """Initialize and return a Supabase client."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)

def upload_to_supabase(file_stream, original_filename, bucket_name="products", prefix=""):
    """
    Uploads a file to Supabase Storage and returns the generated filename.
    If Supabase is not configured, returns None.
    """
    supabase = get_supabase_client()
    if not supabase:
        return None
        
    ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else 'bin'
    unique_filename = f"{prefix}{uuid.uuid4().hex}.{ext}" if prefix else f"{uuid.uuid4().hex}.{ext}"
    
    file_bytes = file_stream.read()
    
    # Upload to Supabase bucket
    # Note: 'file_options' content-type helps browsers render the image properly
    content_type = file_stream.content_type if hasattr(file_stream, 'content_type') else "application/octet-stream"
    
    supabase.storage.from_(bucket_name).upload(
        path=unique_filename,
        file=file_bytes,
        file_options={"content-type": content_type}
    )
    
    return unique_filename

def get_supabase_public_url(filename, bucket_name="products"):
    """Returns the public URL for a given file in a public bucket."""
    supabase = get_supabase_client()
    if not supabase or not filename:
        return None
    
    res = supabase.storage.from_(bucket_name).get_public_url(filename)
    return res

def delete_from_supabase(filename, bucket_name="products"):
    """Deletes a file from a Supabase storage bucket."""
    supabase = get_supabase_client()
    if not supabase or not filename:
        return False
        
    try:
        supabase.storage.from_(bucket_name).remove([filename])
        return True
    except Exception as e:
        print(f"Error deleting from Supabase: {e}")
        return False
