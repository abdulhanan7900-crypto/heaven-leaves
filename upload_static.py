import os
from supabase import create_client
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')
bucket_name = 'heavenleaves'

if not supabase_url or not supabase_key:
    print("❌ Missing Supabase credentials in .env file")
    exit(1)

try:
    supabase = create_client(supabase_url, supabase_key)
    print("[OK] Connected to Supabase")
except Exception as e:
    print(f"[ERROR] Supabase connection failed: {e}")
    exit(1)

def upload_static_files():
    static_dir = Path('staticfiles')
    
    if not static_dir.exists():
        print("[ERROR] staticfiles directory not found. Run: python manage.py collectstatic")
        return
    
    uploaded_count = 0
    error_count = 0
    
    # Use pathlib for better path handling
    for file_path in static_dir.rglob('*'):
        if file_path.is_file():
            # Convert to relative path with forward slashes
            relative_path = file_path.relative_to(static_dir)
            supabase_path = f"static/{relative_path.as_posix()}"  # as_posix() uses forward slashes
            
            print(f"Uploading: {supabase_path}")
            
            try:
                with open(file_path, 'rb') as file_data:
                    supabase.storage.from_(bucket_name).upload(
                        supabase_path, 
                        file_data.read(),
                        {"content-type": "auto"}
                    )
                    uploaded_count += 1
                    print(f"[OK] Success: {supabase_path}")
            except Exception as e:
                error_count += 1
                print(f"[SKIP] {supabase_path} - {str(e)}")
    
    print(f"\nSummary: {uploaded_count} files uploaded, {error_count} errors")

if __name__ == "__main__":
    upload_static_files()