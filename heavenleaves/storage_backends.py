# heavenleaves/storage_backends.py
from supabase import create_client
from django.core.files.storage import Storage
from django.conf import settings
import os

class SupabaseStorage(Storage):
    def __init__(self):
        self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket = settings.SUPABASE_BUCKET

    def _save(self, name, content):
        file_path = f"media/{name}"
        content.seek(0)
        result = self.supabase.storage.from_(self.bucket).upload(file_path, content.read())
        return name

    def exists(self, name):
        try:
            result = self.supabase.storage.from_(self.bucket).list("media")
            files = [item['name'] for item in result]
            return name in files
        except:
            return False

    def url(self, name):
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.bucket}/media/{name}"