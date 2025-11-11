import os
from supabase import create_client
from pathlib import Path

# Get environment variables
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')
bucket_name = 'heavenleaves'

# Check if environment variables are set
if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_KEY environment variables must be set")
    print("Please set these variables and run the script again")
    exit(1)

# Initialize Supabase
try:
    supabase = create_client(supabase_url, supabase_key)
    print("✓ Successfully connected to Supabase")
except Exception as e:
    print(f"✗ Failed to connect to Supabase: {e}")
    exit(1)

def upload_static_files():
    static_dir = 'staticfiles'  # Your collected static files directory
    
    # Check if staticfiles directory exists
    if not os.path.exists(static_dir):
        print(f"Error: {static_dir} directory not found")
        print("Please run 'python manage.py collectstatic' first")
        return
    
    uploaded_count = 0
    error_count = 0
    
    for root, dirs, files in os.walk(static_dir):
        for file in files:
            local_path = os.path.join(root, file)
            
            # Create the path in Supabase (static/folder/file)
            relative_path = os.path.relpath(local_path, static_dir)
            supabase_path = f"static/{relative_path}"
            
            print(f"Uploading {local_path} to {supabase_path}")
            
            try:
                with open(local_path, 'rb') as file_data:
                    # Upload the file
                    result = supabase.storage.from_(bucket_name).upload(
                        supabase_path, 
                        file_data.read(),
                        {"content-type": "auto"}
                    )
                    uploaded_count += 1
                    print(f"✓ Success: {supabase_path}")
            except Exception as e:
                error_count += 1
                print(f"✗ Failed: {supabase_path} - {e}")
    
    print(f"\nUpload completed: {uploaded_count} files uploaded, {error_count} errors")

if __name__ == "__main__":
    upload_static_files()