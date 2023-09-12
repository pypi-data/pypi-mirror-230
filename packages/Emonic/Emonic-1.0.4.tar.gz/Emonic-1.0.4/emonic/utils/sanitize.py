from html.parser import HTMLParser
import re

class SanitizeHTMLParser(HTMLParser):
    def __init__(self, allowed_tags=None, allowed_attributes=None):
        super().__init__()
        self.allowed_tags = allowed_tags or []
        self.allowed_attributes = allowed_attributes or []
        self.sanitized_data = []

    def handle_starttag(self, tag, attrs):
        if tag in self.allowed_tags:
            sanitized_attrs = [(attr, self.sanitize_sql_injection(value)) for attr, value in attrs if attr in self.allowed_attributes]
            sanitized_starttag = "<" + tag + " " + " ".join([attr + '="' + value + '"' for attr, value in sanitized_attrs]) + ">"
            self.sanitized_data.append(sanitized_starttag)

    def handle_endtag(self, tag):
        if tag in self.allowed_tags:
            self.sanitized_data.append("</" + tag + ">")

    def handle_data(self, data):
        self.sanitized_data.append(data)

    @staticmethod
    def sanitize_sql_injection(value):
        return re.sub(r"[\'\";]", '', value)


def sanitize_input(input_string, sanitize_html=True, sanitize_sql=True, sanitize_nosql=True):
    """
    Sanitize input string to prevent HTML, SQL, and NoSQL injection attacks.

    Args:
        input_string (str): The input string to sanitize.
        sanitize_html (bool): Flag to enable HTML sanitization.
        sanitize_sql (bool): Flag to enable SQL sanitization.
        sanitize_nosql (bool): Flag to enable NoSQL sanitization.

    Returns:
        str: The sanitized input string.

    Usage:
        sanitized_string = sanitize_input(user_input, sanitize_html=True, sanitize_sql=True, sanitize_nosql=True)
    """
    if sanitize_html:
        input_string = sanitize_html_input(input_string)

    if sanitize_sql:
        input_string = sanitize_sql_input(input_string)

    if sanitize_nosql:
        input_string = sanitize_nosql_input(input_string)

    return input_string

def sanitize_html_input(input_string):
    """
    Sanitize HTML input string by removing scripts, styles, and enforcing allowed tags and attributes.

    Args:
        input_string (str): The HTML input string to sanitize.

    Returns:
        str: The sanitized HTML string.

    Usage:
        sanitized_html = sanitize_html_input(user_input_html)
    """
    input_string = re.sub(r'<script.*?</script>', '', input_string, flags=re.DOTALL)
    input_string = re.sub(r'<style.*?</style>', '', input_string, flags=re.DOTALL)

    parser = SanitizeHTMLParser(
        allowed_tags=['p', 'br', 'strong', 'em', 'u'],
        allowed_attributes=['href', 'title']
    )
    parser.feed(input_string)

    return ''.join(parser.sanitized_data)

def sanitize_sql_input(input_string):
    """
    Sanitize SQL input string by removing potentially harmful characters.

    Args:
        input_string (str): The SQL input string to sanitize.

    Returns:
        str: The sanitized SQL string.

    Usage:
        sanitized_sql = sanitize_sql_input(user_input_sql)
    """
    return re.sub(r"[\'\";]", '', input_string)

def sanitize_nosql_input(input_string):
    """
    Sanitize NoSQL input string by removing potentially harmful characters.

    Args:
        input_string (str): The NoSQL input string to sanitize.

    Returns:
        str: The sanitized NoSQL string.

    Usage:
        sanitized_nosql = sanitize_nosql_input(user_input_nosql)
    """
    return input_string.replace('$', '').replace('.', '')
