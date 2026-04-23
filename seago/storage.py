import os
from urllib.parse import quote

from django.conf import settings
from django.core.files.storage import FileSystemStorage, Storage
from django.utils.deconstruct import deconstructible


CLOUDINARY_PREFIX = "cloudinary:"


def cloudinary_enabled():
    return bool(os.getenv("CLOUDINARY_URL"))


def is_cloudinary_name(name):
    return isinstance(name, str) and name.startswith(CLOUDINARY_PREFIX)


def encode_cloudinary_name(public_id):
    return f"{CLOUDINARY_PREFIX}{public_id}"


def decode_cloudinary_name(name):
    return name[len(CLOUDINARY_PREFIX) :]


@deconstructible
class HybridMediaStorage(Storage):
    """
    Store checked-in seed media locally and send new uploads to Cloudinary
    whenever CLOUDINARY_URL is configured.
    """

    def __init__(self, *args, **kwargs):
        self.local_storage = FileSystemStorage(
            location=settings.MEDIA_ROOT,
            base_url=settings.MEDIA_URL,
        )

    def _save(self, name, content):
        if not cloudinary_enabled():
            return self.local_storage._save(name, content)

        from cloudinary import uploader

        folder = os.path.dirname(name).replace("\\", "/").strip("/") or None
        if hasattr(content, "seek"):
            content.seek(0)

        upload_result = uploader.upload(
            content,
            folder=folder,
            resource_type="image",
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )
        return encode_cloudinary_name(upload_result["public_id"])

    def delete(self, name):
        if not name:
            return

        if is_cloudinary_name(name):
            from cloudinary import uploader

            uploader.destroy(
                decode_cloudinary_name(name),
                resource_type="image",
                invalidate=True,
            )
            return

        self.local_storage.delete(name)

    def exists(self, name):
        if is_cloudinary_name(name):
            return False
        return self.local_storage.exists(name)

    def open(self, name, mode="rb"):
        if is_cloudinary_name(name):
            raise NotImplementedError("Cloudinary-backed files are not opened locally.")
        return self.local_storage.open(name, mode)

    def path(self, name):
        if is_cloudinary_name(name):
            raise NotImplementedError("Cloudinary-backed files do not have a local path.")
        return self.local_storage.path(name)

    def size(self, name):
        if is_cloudinary_name(name):
            from cloudinary import api

            resource = api.resource(decode_cloudinary_name(name), resource_type="image")
            return resource["bytes"]
        return self.local_storage.size(name)

    def url(self, name):
        if not name:
            return ""

        if is_cloudinary_name(name):
            from cloudinary.utils import cloudinary_url

            url, _ = cloudinary_url(
                decode_cloudinary_name(name),
                resource_type="image",
                secure=True,
            )
            return url

        if name.startswith(("http://", "https://")):
            return name

        base_url = self.local_storage.base_url or settings.MEDIA_URL
        return f"{base_url.rstrip('/')}/{quote(name.lstrip('/'))}"
