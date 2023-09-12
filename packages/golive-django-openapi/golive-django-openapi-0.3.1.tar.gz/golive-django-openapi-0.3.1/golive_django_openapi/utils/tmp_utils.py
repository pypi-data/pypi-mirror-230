# Author: kk.Fang(fkfkbill@gmail.com)

__all__ = [
    "TempFile"
]

from pathlib import Path
import hashlib
import time
import os

from django.conf import settings


class TempFile:

    TEMP_PREFIX = settings.STATICFILES_DIRS[0]

    def __init__(self, ext: str, not_delete: bool = False, **kwargs):

        assert ext
        self.ext = ext
        self.not_delete = not_delete
        self.short_filename = f"{hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()}{ext}"
        self.filename = str(
            Path(self.TEMP_PREFIX) / self.short_filename
        )
        self._kwargs = kwargs
        self.file = open(self.filename, **kwargs)

    def reopen(self, **kwargs):
        self.file.close()
        self.file = open(self.filename, **{**self._kwargs, **kwargs})

    @property
    def url(self):
        """relative url"""
        return str(Path(settings.STATIC_URL_TO_USER) / self.short_filename)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        if not self.not_delete:
            try:
                os.remove(self.filename)
            except:
                pass
