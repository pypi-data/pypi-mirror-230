import os
from urllib.parse import urljoin
from jinja2 import Environment, FileSystemLoader
from emonic.components.blueprint import Blueprint

class Freeze:
    def __init__(self, app):
        self.app = app
        self.output_folder = 'frozen'

    def freeze(self):
        os.makedirs(self.output_folder, exist_ok=True)

        with self.app.app_context():
            self.freeze_routes()
            self.freeze_blueprints()

        print("Freezing complete.")

    def freeze_routes(self):
        with self.app.app_context():
            for rule in self.app.url_map.iter_rules():
                if rule.endpoint != 'static':
                    self.freeze_url(rule.rule)

    def freeze_blueprints(self):
        for blueprint in self.app.blueprints:
            if isinstance(blueprint, Blueprint):
                with self.app.app_context():
                    for rule in blueprint.url_map.iter_rules():
                        if rule.endpoint != 'static':
                            self.freeze_url(rule.rule, blueprint=blueprint.name)

    def freeze_url(self, url, blueprint=None):
        print(f"Freezing: {url}")
        endpoint = url.strip('/').replace('/', '.')
        if blueprint:
            endpoint = f"{blueprint}.{endpoint}"
        with self.app.test_request_context(url):
            self._create_static_file(url, endpoint)

    def _create_static_file(self, url, endpoint):
        static_file_path = os.path.join(self.output_folder, url.lstrip('/'))
        response = self.app.handle_request(self.app.request)
        with open(static_file_path, 'wb') as f:
            f.write(response.data)

    def clean_output_folder(self):
        for filename in os.listdir(self.output_folder):
            file_path = os.path.join(self.output_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error cleaning up file: {file_path} - {e}")

    def generate_unique_filename(self, url):
        url_hash = hash(url)
        return f"{url_hash}.html"

    def generate_static_url(self, url):
        return urljoin(self.app.url_for_static(self.output_folder), self.generate_unique_filename(url))

    def render_template_to_file(self, template_name, output_filename, **context):
        template = self.app.template_env.get_template(template_name)
        rendered_content = template.render(**context)
        with open(os.path.join(self.output_folder, output_filename), 'w') as f:
            f.write(rendered_content)

    def generate_custom_static_files(self):
        custom_static_files = [
            {'template': 'custom_page.html', 'output': 'custom_page.html'},
            # Add more custom templates here
        ]
        with self.app.app_context():
            for file_info in custom_static_files:
                self.render_template_to_file(file_info['template'], file_info['output'])

    def register_generator(self, generator_func):
        self.generator_func = generator_func

    def freeze_with_generator(self):
        os.makedirs(self.output_folder, exist_ok=True)

        with self.app.app_context():
            self.freeze_routes_with_generator()
            self.freeze_blueprints_with_generator()

        print("Freezing with generator complete.")

    def freeze_routes_with_generator(self):
        if not hasattr(self, 'generator_func'):
            raise ValueError("Generator function is not registered.")

        with self.app.app_context():
            for url in self.generator_func():
                self.freeze_url(url)

    def freeze_blueprints_with_generator(self):
        for blueprint in self.app.blueprints:
            if isinstance(blueprint, Blueprint):
                if hasattr(blueprint, 'generator_func'):
                    with self.app.app_context():
                        for url in blueprint.generator_func():
                            self.freeze_url(url, blueprint=blueprint.name)

    def generate_sitemap(self, filename='sitemap.xml'):
        sitemap_path = os.path.join(self.output_folder, filename)
        with open(sitemap_path, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')

            with self.app.app_context():
                for rule in self.app.url_map.iter_rules():
                    if rule.endpoint != 'static':
                        url = self.url_for(rule.endpoint)
                        f.write(f'  <url>\n')
                        f.write(f'    <loc>{url}</loc>\n')
                        f.write(f'  </url>\n')

            f.write('</urlset>')

    def generate_robots_txt(self, filename='robots.txt'):
        robots_txt_path = os.path.join(self.output_folder, filename)
        with open(robots_txt_path, 'w') as f:
            f.write('User-agent: *\n')
            f.write('Disallow:\n')
