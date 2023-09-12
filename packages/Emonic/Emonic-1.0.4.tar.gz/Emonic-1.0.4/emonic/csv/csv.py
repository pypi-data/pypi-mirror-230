import csv
import os
import mimetypes
from io import StringIO
from ..core import Response
from ..contrib import JsonResponse as jsonify
import os.path as op

class CSV:
    def __init__(self, app=None):
        self.app = app
        self.delimiter = ','
        self.encoding = 'utf-8'
        self.mimetypes = {
            'csv': 'text/csv',
            'txt': 'text/plain'
        }
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.app.add_url_rule('/download_csv', 'download_csv', self.download_csv)

    def set_delimiter(self, delimiter):
        self.delimiter = delimiter

    def set_encoding(self, encoding):
        self.encoding = encoding

    def set_mimetype(self, extension, mimetype):
        self.mimetypes[extension] = mimetype

    def get_mimetype(self, filename):
        extension = filename.split('.')[-1]
        return self.mimetypes.get(extension, 'text/csv')

    def validate_data(self, data):
        if not isinstance(data, (list, tuple)):
            raise ValueError("Data must be a list or tuple of rows.")
        if not all(isinstance(row, (dict, list, tuple)) for row in data):
            raise ValueError("Each row must be a dictionary or a list/tuple.")
        if isinstance(data[0], dict):
            if not all(isinstance(cell, str) for cell in data[0]):
                raise ValueError("Dictionary-based rows must contain string keys.")
        elif isinstance(data[0], (list, tuple)):
            if not all(isinstance(cell, str) for cell in data[0]):
                raise ValueError("List/tuple-based rows must contain string values.")
        else:
            raise ValueError("Unsupported row format.")

    def generate_csv(self, rows, headers=None, include_header=True):
        output = StringIO()
        csv_writer = csv.writer(output, delimiter=self.delimiter)

        if headers and include_header:
            csv_writer.writerow(headers)

        for row in rows:
            if isinstance(row, dict):
                csv_writer.writerow(row.values())
            else:
                csv_writer.writerow(row)

        return output.getvalue().encode(self.encoding)

    def download_csv(self, rows, filename='data.csv', headers=None, mimetype=None, include_header=True):
        self.validate_data(rows)
        if not mimetype:
            mimetype = self.get_mimetype(filename)
        response = Response(self.generate_csv(rows, headers, include_header), content_type=mimetype)
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    def serialize_csv(self, rows, headers=None):
        if headers and isinstance(rows[0], dict):
            rows.insert(0, headers)
        serialized = StringIO()
        writer = csv.DictWriter(serialized, fieldnames=headers or rows[0].keys())
        writer.writerows(rows)
        return serialized.getvalue()

    def jsonify_csv(self, rows, headers=None):
        serialized = self.serialize_csv(rows, headers)
        return jsonify(data=serialized)

    def send_csv(self, rows, filename='data.csv', headers=None):
        response = self.generate_csv(rows, headers)
        mimetype = self.get_mimetype(filename)
        return Response(response, content_type=mimetype)

    def send_jsonified_csv(self, rows, filename='data.csv', headers=None):
        serialized = self.serialize_csv(rows, headers)
        return jsonify(data=serialized)

    def send_csv_string(self, csv_string, filename='data.csv', as_attachment=True):
        mimetype = self.get_mimetype(filename)
        return self.generate_response(csv_string, filename, mimetype, as_attachment)

    def send_jsonified_csv_string(self, csv_string, filename='data.csv'):
        mimetype = 'application/json'
        return self.generate_response(csv_string, f'{filename}.json', mimetype)

    def send_csv_data(self, data, filename='data.csv', as_attachment=True):
        csv_content = self.generate_csv(data)
        return self.send_csv_string(csv_content, filename, as_attachment)

    def send_jsonified_csv_data(self, data, filename='data.csv'):
        csv_content = self.serialize_csv(data)
        return self.send_jsonified_csv_string(csv_content, filename)

    def download_csv_data(self, data, filename='data.csv'):
        csv_content = self.generate_csv(data)
        mimetype = self.get_mimetype(filename)
        return self.generate_response(csv_content, filename, mimetype)

    def download_jsonified_csv_data(self, data, filename='data.csv'):
        csv_content = self.serialize_csv(data)
        mimetype = 'application/json'
        return self.generate_response(csv_content, f'{filename}.json', mimetype)

    def generate_response(self, data, filename, mimetype, as_attachment=True):
        response = Response(data, content_type=mimetype)
        if as_attachment:
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    def send_csv_file_response(self, file_path, as_attachment=True):
        filename = op.basename(file_path)
        mimetype = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        with open(file_path, 'rb') as f:
            file_content = f.read()
        return self.generate_response(file_content, filename, mimetype, as_attachment)

    def jsonify_csv_file_response(self, file_path):
        filename = op.basename(file_path)
        mimetype = 'application/json'
        with open(file_path, 'rb') as f:
            file_content = self.serialize_csv(f)
        return self.generate_response(file_content, f'{filename}.json', mimetype)
