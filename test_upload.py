import os
from app import create_app, db
from models import Product
from utils import upload_to_supabase, get_supabase_public_url
import tempfile

app = create_app()
app.app_context().push()

class DummyImage:
    def __init__(self, data, filename):
        self.data = data
        self.filename = filename
    def read(self):
        return self.data
    def seek(self, pos):
        pass

fake_img = DummyImage(b"fake_image_bytes", "test_item.jpg")

print("Uploading to Supabase Storage...")
bucket = "products"
supabase_filename = upload_to_supabase(fake_img, fake_img.filename, bucket_name=bucket, prefix="test_")

if supabase_filename:
    print(f"Uploaded successfully as: {supabase_filename}")
    pub_url = get_supabase_public_url(supabase_filename, bucket)
    print(f"Public URL: {pub_url}")
    
    p = Product(
        name="Test API Bangle",
        description="This product was added via the python script to test the live Supabase API Integration.",
        price=1299.00,
        stock=5,
        image_url=pub_url if isinstance(pub_url, str) else supabase_filename
    )
    db.session.add(p)
    db.session.commit()
    print("Added test product to PostgreSQL!")
else:
    print("Failed to upload to Supabase.")
