"""Set up file cache"""

from io import BytesIO

from django.core.cache import caches
from django.core.files.uploadedfile import InMemoryUploadedFile

def get_cache(cache_name):
    """get a cache from a name"""
    return caches[cache_name]

class FileCache():
    """The file cache for storing files temporarily"""

    def __init__(self):
        self.backend = self.get_backend()

    def get_backend(self):
        """get the file_resubmit cache"""
        return get_cache("file_resubmit")

    def set(self, key, upload):
        """add a file to the cache"""
        upload.file.seek(0)
        state = {
            "name": upload.name,
            "size": upload.size,
            "content_type": upload.content_type,
            "charset": upload.charset,
            "content": upload.file.read(),
        }
        upload.file.seek(0)
        self.backend.set(key, state)

    def get(self, key, field_name):
        """get a file from the cache"""
        upload = None
        state = self.backend.get(key)
        if state:
            f = BytesIO()
            f.write(state["content"])
            upload = InMemoryUploadedFile(
                file=f,
                field_name=field_name,
                name=state["name"],
                content_type=state["content_type"],
                size=state["size"],
                charset=state["charset"],
            )
            upload.file.seek(0)
        return upload

    def delete(self, key):
        """remove a file from the cache using its key"""
        self.backend.delete(key)
