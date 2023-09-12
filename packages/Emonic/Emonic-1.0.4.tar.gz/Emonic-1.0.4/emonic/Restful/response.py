import json
import xml.etree.ElementTree as ET
from html import escape

class ApiResponse:
    def __init__(self, data=None, message=None, status_code=200, headers=None, metadata=None, content_type='application/json'):
        """
        Initialize an ApiResponse instance.

        :param data: The data to include in the response.
        :param message: A message or description about the response.
        :param status_code: The HTTP status code for the response (default is 200 OK).
        :param headers: Additional headers to include in the response.
        :param metadata: Metadata to include in the response for additional information.
        :param content_type: The content type of the response (e.g., 'application/json', 'application/xml').
        """
        self.data = data
        self.message = message
        self.status_code = status_code
        self.headers = headers or {}
        self.metadata = metadata or {}
        self.content_type = content_type

    def to_dict(self):
        """
        Convert the ApiResponse instance to a dictionary for serialization.

        :return: A dictionary representation of the ApiResponse.
        """
        response_dict = {
            'data': self.data,
            'message': self.message,
            'status_code': self.status_code,
            'metadata': self.metadata,
        }
        return response_dict

    def add_header(self, key, value):
        """
        Add a custom header to the response.

        :param key: The header key.
        :param value: The header value.
        """
        self.headers[key] = value

    @classmethod
    def error(cls, message, status_code=400, content_type='application/json'):
        """
        Create an error response.

        :param message: The error message.
        :param status_code: The HTTP status code for the error response (default is 400 Bad Request).
        :param content_type: The content type of the response.
        :return: An ApiResponse instance representing an error response.
        """
        return cls(data=None, message=message, status_code=status_code, content_type=content_type)

    @classmethod
    def paginate(cls, data, message='Success', status_code=200, headers=None, metadata=None, page=None, per_page=None, total_items=None, content_type='application/json'):
        """
        Create a paginated response.

        :param data: The paginated data.
        :param message: A message or description about the response.
        :param status_code: The HTTP status code for the response (default is 200 OK).
        :param headers: Additional headers to include in the response.
        :param metadata: Metadata to include in the response for additional information.
        :param page: The current page number (optional).
        :param per_page: The number of items per page (optional).
        :param total_items: The total number of items (optional).
        :param content_type: The content type of the response.
        :return: An ApiResponse instance representing a paginated response.
        """
        metadata = metadata or {}
        if page is not None:
            metadata['page'] = page
        if per_page is not None:
            metadata['per_page'] = per_page
        if total_items is not None:
            metadata['total_items'] = total_items
            metadata['total_pages'] = (total_items + per_page - 1) // per_page

        return cls(data=data, message=message, status_code=status_code, headers=headers, metadata=metadata, content_type=content_type)

    def serialize(self):
        """
        Serialize the response data based on the specified content type.

        :return: The serialized response data as a string.
        """
        if self.content_type == 'application/json':
            return json.dumps(self.to_dict())
        elif self.content_type == 'application/xml':
            return self.serialize_xml()
        elif self.content_type == 'text/html':
            return self.serialize_html()
        elif self.content_type == 'text/plain':
            return str(self.data)

    def serialize_xml(self):
        """
        Serialize the response data to XML.

        :return: The serialized response data as an XML string.
        """
        root = ET.Element('response')
        self.build_xml_element(root, self.data)

        xml_str = ET.tostring(root, encoding='utf-8', method='xml')
        return xml_str.decode('utf-8')

    def build_xml_element(self, parent, data):
        # Recursive method to build XML elements from dictionary data
        if isinstance(data, dict):
            for key, value in data.items():
                element = ET.SubElement(parent, key)
                self.build_xml_element(element, value)
        elif isinstance(data, list):
            for item in data:
                element = ET.SubElement(parent, 'item')
                self.build_xml_element(element, item)
        else:
            parent.text = str(data)

    def serialize_html(self):
        """
        Serialize the response data to an HTML string.

        :return: The serialized response data as an HTML string.
        """
        if 'html' in self.data:
            return self.data['html']

        # Create a basic HTML response with the data as the body content
        html_str = f"<html><body>{escape(str(self.data))}</body></html>"
        return html_str

    @classmethod
    def wrap(cls, data, message='Success', status_code=200, headers=None, metadata=None, content_type='application/json'):
        """
        Wrap and format the response data.

        :param data: The data to include in the response.
        :param message: A message or description about the response.
        :param status_code: The HTTP status code for the response (default is 200 OK).
        :param headers: Additional headers to include in the response.
        :param metadata: Metadata to include in the response for additional information.
        :param content_type: The content type of the response.
        :return: An ApiResponse instance representing the formatted response.
        """
        response_data = {
            'data': data,
            'message': message,
            'status_code': status_code,
            'metadata': metadata or {},
        }
        return cls(data=response_data, headers=headers, content_type=content_type)
