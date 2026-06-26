# heavenleaves/storage_backends.py
from supabase import create_client
from django.core.files.storage import Storage
from django.conf import settings
import os
import mimetypes


class SupabaseStorage(Storage):
    def __init__(self):
        self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket = settings.SUPABASE_BUCKET

    def _save(self, name, content):
        # name is like 'categories/image.jpg' or 'products/photo.png'
        file_path = f"media/{name}"
        content.seek(0)
        data = content.read()
        # Detect content type
        mime_type, _ = mimetypes.guess_type(name)
        if not mime_type:
            mime_type = 'application/octet-stream'
        try:
            # Try upload first
            self.supabase.storage.from_(self.bucket).upload(
                file_path, data, {'content-type': mime_type, 'upsert': 'true'}
            )
        except Exception:
            # If file exists, update it
            try:
                self.supabase.storage.from_(self.bucket).remove([file_path])
                self.supabase.storage.from_(self.bucket).upload(
                    file_path, data, {'content-type': mime_type}
                )
            except Exception:
                pass
        return name

    def exists(self, name):
        # Always return False so Django generates unique names via get_available_name
        return False

    def url(self, name):
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.bucket}/media/{name}"

    def delete(self, name):
        file_path = f"media/{name}"
        try:
            self.supabase.storage.from_(self.bucket).remove([file_path])
        except Exception:
            pass

    def size(self, name):
        return 0
