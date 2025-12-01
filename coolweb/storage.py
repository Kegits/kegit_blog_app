"""
Custom storage backend that uses Cloudinary API directly, bypassing django-cloudinary-storage
which has fallback bugs on read-only filesystems like Vercel.
"""
import os
import io
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
import cloudinary
import cloudinary.uploader
import cloudinary.api


class CloudinaryDirectStorage(Storage):
    """
    Storage backend that uploads files directly to Cloudinary via API.
    Bypasses django-cloudinary-storage to avoid fallback-to-filesystem bugs.
    """

    def _open(self, name, mode='rb'):
        """Open a file from Cloudinary (not implemented for simplicity)."""
        raise NotImplementedError("Direct file reading from Cloudinary not supported")

    def _save(self, name, content):
        """
        Upload a file to Cloudinary using the API.
        """
        # Ensure cloudinary is configured
        if not cloudinary.config().cloud_name:
            raise ValueError("Cloudinary not configured. Set CLOUDINARY_CLOUD_NAME env var.")

        # Read the file content into bytes
        if hasattr(content, 'read'):
            file_content = content.read()
            if isinstance(file_content, str):
                file_content = file_content.encode('utf-8')
        else:
            file_content = content
            if isinstance(file_content, str):
                file_content = file_content.encode('utf-8')

        # Determine the folder/resource type from the filename
        # e.g., "profile_pics/image.jpg" -> folder="profile_pics"
        folder = os.path.dirname(name)
        base_name = os.path.basename(name)
        name_without_ext = os.path.splitext(base_name)[0]

        # Upload to Cloudinary
        try:
            # Create a file-like object from bytes for cloudinary
            file_obj = io.BytesIO(file_content) if isinstance(file_content, bytes) else file_content
            
            result = cloudinary.uploader.upload(
                file_obj,
                folder=folder if folder else 'media',
                public_id=name_without_ext,
                resource_type='auto',
                overwrite=True,
                unique_filename=False,
            )
            # Return the full public_id (includes folder)
            public_id = result.get('public_id')
            return public_id
        except Exception as e:
            # Log the error but don't silently fail
            import traceback
            print(f"ERROR: Cloudinary upload failed for {name}: {str(e)}")
            traceback.print_exc()
            raise IOError(f"Cloudinary upload failed: {str(e)}")

    def url(self, name):
        """
        Return the Cloudinary URL for a file.
        """
        if not name:
            return ''
        # Construct Cloudinary URL
        cloud_name = cloudinary.config().cloud_name
        if not cloud_name:
            raise ValueError("CLOUDINARY_CLOUD_NAME not configured")
        # Use the public_id returned by _save
        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{name}"

    def exists(self, name):
        """
        Check if a file exists in Cloudinary.
        """
        # For simplicity, assume it exists if we have a name
        # A more robust implementation would call cloudinary.api.resource(name)
        return bool(name)

    def delete(self, name):
        """
        Delete a file from Cloudinary.
        """
        try:
            cloudinary.uploader.destroy(name, resource_type='image')
        except Exception as e:
            # Silently fail for deletes (resource might not exist)
            pass

    def get_available_name(self, name, max_length=None):
        """
        Generate a unique filename.
        """
        # Cloudinary handles uniqueness, so just return the name
        return name

    def get_accessed_time(self, name):
        """Not implemented."""
        raise NotImplementedError

    def get_created_time(self, name):
        """Not implemented."""
        raise NotImplementedError

    def get_modified_time(self, name):
        """Not implemented."""
        raise NotImplementedError

    def listdir(self, path):
        """Not implemented."""
        raise NotImplementedError

    def size(self, name):
        """Not implemented."""
        raise NotImplementedError

