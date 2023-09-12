import os
from werkzeug.utils import secure_filename
import mimetypes

class UploadSet:
    def __init__(self, name, extensions=None, default_dest=None):
        self.name = name
        self.extensions = extensions
        self.default_dest = default_dest
        self.config = {}

    def configure(self, app, **options):
        self.config.update(options)

    def save(self, storage, filename=None, folder=None):
        if filename:
            filename = secure_filename(filename)
        else:
            raise ValueError("Filename must be provided.")

        if self.extensions and not self.is_allowed_file(filename):
            raise ValueError(f"File extension not allowed for {filename}")

        if folder:
            destination = os.path.join(self.config.get(folder, self.default_dest), filename)
        else:
            destination = os.path.join(self.default_dest, filename)

        storage.save(destination)

    def is_allowed_file(self, filename):
        if self.extensions is None:
            return True
        return '.' in filename and filename.rsplit('.', 1)[1] in self.extensions

    def get_uploaded_file_path(self, filename):
        return os.path.join(self.default_dest, filename)

    def delete(self, filename):
        file_path = self.get_uploaded_file_path(filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise FileNotFoundError(f"File '{filename}' not found.")

    def list_uploaded_files(self):
        return os.listdir(self.default_dest)

    def file_exists(self, filename):
        return os.path.exists(self.get_uploaded_file_path(filename))

    def get_file_size(self, filename):
        file_path = self.get_uploaded_file_path(filename)
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        else:
            raise FileNotFoundError(f"File '{filename}' not found.")

    def get_file_extension(self, filename):
        if '.' in filename:
            return filename.rsplit('.', 1)[1]
        else:
            raise ValueError("Filename has no extension.")

    def generate_unique_filename(self, filename):
        base_name, extension = os.path.splitext(filename)
        counter = 1
        while self.file_exists(filename):
            filename = f"{base_name}_{counter}{extension}"
            counter += 1
        return filename

    def save_with_unique_filename(self, storage, filename=None, folder=None):
        if filename:
            filename = self.generate_unique_filename(filename)
        self.save(storage, filename, folder)
        return filename

    def get_uploaded_files_with_metadata(self):
        files_metadata = []
        for file_name in self.list_uploaded_files():
            file_metadata = {
                'filename': file_name,
                'size': self.get_file_size(file_name),
                'extension': self.get_file_extension(file_name),
                'path': self.get_uploaded_file_path(file_name),
                'url': self.get_file_url(file_name)
            }
            files_metadata.append(file_metadata)
        return files_metadata

    def get_file_url(self, filename):
        return f"/uploads/{filename}"  # Customize this based on your app's URL structure

    def __getitem__(self, filename):
        return self.get_uploaded_file_path(filename)

    def __iter__(self):
        return iter(self.list_uploaded_files())

    def save_multiple(self, storage_list, filenames=None, folder=None):
        if filenames and len(storage_list) != len(filenames):
            raise ValueError("Number of filenames must match the number of storage objects.")
        
        saved_files = []
        for i, storage in enumerate(storage_list):
            filename = filenames[i] if filenames else None
            saved_filename = self.save_with_unique_filename(storage, filename, folder)
            saved_files.append(saved_filename)
        
        return saved_files

    def get_files_by_extension(self, extension):
        return [file for file in self.list_uploaded_files() if file.endswith(f".{extension}")]

    def get_file_metadata(self, filename):
        if not self.file_exists(filename):
            raise FileNotFoundError(f"File '{filename}' not found.")
        
        file_path = self.get_uploaded_file_path(filename)
        metadata = {
            'filename': filename,
            'size': self.get_file_size(filename),
            'extension': self.get_file_extension(filename),
            'path': file_path,
            'url': self.get_file_url(filename),
            'mime_type': self.get_file_mime_type(filename),
        }
        return metadata

    def get_file_mime_type(self, filename):
        if not self.file_exists(filename):
            raise FileNotFoundError(f"File '{filename}' not found.")
        
        file_path = self.get_uploaded_file_path(filename)
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type
