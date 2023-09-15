from abc import ABC

from django.conf import settings
from django.core.files.storage import Storage
from django.forms import ValidationError
from termcolor import colored

from virtualpreference.storage.core import VPStorage


class VPBucket(Storage, VPStorage, ABC):
    """
    The VPBucket is a special support for django storage system.
    for raw implementation guide will be available soon with the
    class name VPStorage.
    """

    def __init__(self):
        super().__init__()
        try:
            self.api_key = settings.VPSTORAGE_API_KEY
        except AttributeError:
            msg = "Warning: Please supply VPSTORAGE_API_KEY "
            "in your settings file or for support "
            "write an email us on error@virtualpreference.com"

            print(colored(msg, "red"))
            raise ValidationError(msg)

    def delete(self, name):
        if settings.DEBUG:
            print(colored(
                f"VPRS: Deleted FR: {name}", "green"
            ))

    def save(self, name, content, max_length=None):
        r = self.push(name, content.content_type, content)
        if settings.DEBUG:
            print(colored(
                f"VPRS: Accepted "
                f"FR: {r['fileInfo']['uuid']} "
                f"FN: {r['fileInfo']['name']} "
                f"FM: {r['fileInfo']['mime']} "
                f"FS: {r['fileInfo']['size']}", "green"
            ))
        return f"{r['fileInfo']['uuid']}"

    def url(self, name):
        return f"https://bucket.virtualpreference.com/" \
               f"v1/storage/read?f={name}"

    def exists(self, name):
        return False
