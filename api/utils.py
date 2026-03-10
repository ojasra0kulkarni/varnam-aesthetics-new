import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import threading
import os
import uuid
import urllib.request
import urllib.error
import json


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


def upload_to_supabase(file_stream, original_filename, bucket_name="products", prefix=""):
    """
    Uploads a file to Supabase Storage using the REST API (no SDK needed).
    If Supabase is not configured, returns None.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        return None

    ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else 'bin'
    unique_filename = f"{prefix}{uuid.uuid4().hex}.{ext}" if prefix else f"{uuid.uuid4().hex}.{ext}"

    file_bytes = file_stream.read()

    content_type = file_stream.content_type if hasattr(file_stream, 'content_type') else "application/octet-stream"

    upload_url = f"{url}/storage/v1/object/{bucket_name}/{unique_filename}"

    try:
        req = urllib.request.Request(
            upload_url,
            data=file_bytes,
            method='POST',
            headers={
                'Authorization': f'Bearer {key}',
                'apikey': key,
                'Content-Type': content_type,
            }
        )
        urllib.request.urlopen(req)
        return unique_filename
    except Exception as e:
        print(f"Supabase upload failed: {e}. Falling back to local storage.")
        return None


def get_supabase_public_url(filename, bucket_name="products"):
    """Returns the public URL for a given file in a public bucket."""
    url = os.environ.get("SUPABASE_URL")
    if not url or not filename:
        return None
    return f"{url}/storage/v1/object/public/{bucket_name}/{filename}"


def delete_from_supabase(filename, bucket_name="products"):
    """Deletes a file from a Supabase storage bucket using the REST API."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key or not filename:
        return False

    try:
        delete_url = f"{url}/storage/v1/object/{bucket_name}/{filename}"
        req = urllib.request.Request(
            delete_url,
            method='DELETE',
            headers={
                'Authorization': f'Bearer {key}',
                'apikey': key,
            }
        )
        urllib.request.urlopen(req)
        return True
    except Exception as e:
        print(f"Error deleting from Supabase: {e}")
        return False
