import os
import mimetypes
import hashlib
from werkzeug.wrappers import Response
from werkzeug.exceptions import NotFound

class Assets:
    def __init__(self, app=None):
        """
        Initialize the Assets manager.

        Args:
            app: The Flask app (optional).

        Usage:
            assets = Assets(app)
        """
        self._bundles = {}
        self._processors = {}
        self._manifest = {}
        self._cache_busting = False
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize the Flask app with this Assets manager.

        Args:
            app: The Flask app.

        Usage:
            assets.init_app(app)
        """
        self.app = app
        app.assets = self

    def serve_static(self, filename):
        """
        Serve a static asset.

        Args:
            filename (str): The filename of the static asset.

        Returns:
            Response: The response containing the static asset.

        Raises:
            NotFound: If the asset is not found.

        Usage:
            response = assets.serve_static('style.css')
        """
        static_path = os.path.join(self.app.static_folder, filename)
        if os.path.isfile(static_path):
            mimetype, _ = mimetypes.guess_type(static_path)
            if mimetype:
                return Response(open(static_path, 'rb').read(), mimetype=mimetype)
        raise NotFound()

    def url_for_static(self, filename):
        """
        Get the URL for a static asset.

        Args:
            filename (str): The filename of the static asset.

        Returns:
            str: The URL for the static asset.

        Usage:
            url = assets.url_for_static('style.css')
        """
        return f'/static/{filename}'

    def register_bundle(self, name, *assets):
        """
        Register a bundle of assets.

        Args:
            name (str): The name of the bundle.
            *assets: Variable number of asset filenames.

        Usage:
            assets.register_bundle('main', 'style.css', 'script.js')
        """
        self._bundles[name] = assets

    def get_bundle_urls(self, name):
        """
        Get URLs for assets in a bundle.

        Args:
            name (str): The name of the bundle.

        Returns:
            list: List of asset URLs.

        Usage:
            urls = assets.get_bundle_urls('main')
        """
        urls = []
        assets = self._bundles.get(name, [])
        for asset in assets:
            urls.append(self.url_for_static(asset))
        return urls

    def generate_bundle_hash(self, name):
        """
        Generate a hash for a bundle of assets.

        Args:
            name (str): The name of the bundle.

        Returns:
            str: The generated hash.

        Usage:
            hash_value = assets.generate_bundle_hash('main')
        """
        assets = self._bundles.get(name, [])
        hash_content = ''.join(open(os.path.join(self.app.static_folder, asset), 'rb').read() for asset in assets)
        return hashlib.md5(hash_content.encode('utf-8')).hexdigest()

    def url_for_bundle(self, name):
        """
        Get the URL for a bundle of assets with cache busting.

        Args:
            name (str): The name of the bundle.

        Returns:
            str: The URL for the bundle.

        Usage:
            url = assets.url_for_bundle('main')
        """
        hash_value = self.generate_bundle_hash(name)
        return f'/static/bundles/{name}_{hash_value}.bundle'

    def add_processor(self, file_extension, processor):
        """
        Add a processor for a specific file extension.

        Args:
            file_extension (str): The file extension.
            processor (callable): The processor function.

        Usage:
            assets.add_processor('.scss', compile_scss)
        """
        self._processors[file_extension] = processor

    def process_asset(self, asset):
        """
        Process an asset using a registered processor.

        Args:
            asset (str): The filename of the asset.

        Returns:
            str: The processed asset filename.

        Usage:
            processed_asset = assets.process_asset('style.scss')
        """
        extension = os.path.splitext(asset)[1]
        processor = self._processors.get(extension)
        if processor:
            return processor(asset)
        return asset

    def url_for_processed(self, asset):
        """
        Get the URL for a processed asset.

        Args:
            asset (str): The filename of the processed asset.

        Returns:
            str: The URL for the processed asset.

        Usage:
            url = assets.url_for_processed('style.css')
        """
        processed_asset = self.process_asset(asset)
        return self.url_for_static(processed_asset)

    def enable_cache_busting(self):
        """
        Enable cache busting for assets.

        Usage:
            assets.enable_cache_busting()
        """
        self._cache_busting = True

    def add_manifest_entry(self, original_path, hashed_path):
        """
        Add an entry to the assets manifest.

        Args:
            original_path (str): The original path of the asset.
            hashed_path (str): The hashed path of the asset.

        Usage:
            assets.add_manifest_entry('style.css', 'style_hashed.css')
        """
        self._manifest[original_path] = hashed_path

    def url_for_manifest(self, original_path):
        """
        Get the URL for an asset from the assets manifest.

        Args:
            original_path (str): The original path of the asset.

        Returns:
            str: The URL for the asset.

        Usage:
            url = assets.url_for_manifest('style.css')
        """
        if self._cache_busting:
            hashed_path = self._manifest.get(original_path)
            if hashed_path:
                return self.url_for_static(hashed_path)
        return self.url_for_static(original_path)
