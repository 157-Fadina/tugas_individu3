import os
from dotenv import load_dotenv
from database import get_engine, init_db
import models 

load_dotenv()

print("Mencoba koneksi ke database...")
try:
    url = os.getenv("DATABASE_URL")
    print(f"URL: {url}")
    
    settings = {'sqlalchemy.url': url}
    engine = get_engine(settings)
    
    print("Membuat tabel...")
    init_db(engine)
    
    print("SUKSES! Tabel 'reviews' berhasil dibuat di database.")
except Exception as e:
    print(f"❌ GAGAL: {e}")