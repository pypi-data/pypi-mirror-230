from werkzeug.exceptions import BadRequest

class Fields:
    def __init__(self, fields):
        self.fields = fields

    def format(self, data):
        formatted_data = {}
        for field_name, field_info in self.fields.items():
            field_type = field_info.get('type', str)
            default_value = field_info.get('default')
            nullable = field_info.get('nullable', False)

            if field_name in data:
                value = data[field_name]
                if value is None and nullable:
                    formatted_data[field_name] = None
                else:
                    try:
                        formatted_data[field_name] = field_type(value)
                    except (ValueError, TypeError):
                        raise BadRequest(f"Invalid data type for field '{field_name}'")
            elif default_value is not None:
                formatted_data[field_name] = default_value
            elif not nullable:
                raise BadRequest(f"Missing required field '{field_name}'")

        return formatted_data

    def validate(self, data):
        for field_name, field_info in self.fields.items():
            required = field_info.get('required', True)
            nullable = field_info.get('nullable', False)
            value = data.get(field_name)

            if required and (value is None or (not nullable and value == '')):
                raise BadRequest(f"Missing required field '{field_name}'")

            field_type = field_info.get('type', str)
            choices = field_info.get('choices')
            if choices and value not in choices:
                raise BadRequest(f"Invalid value for field '{field_name}'")

            max_length = field_info.get('max_length')
            if max_length is not None and len(str(value)) > max_length:
                raise BadRequest(f"Field '{field_name}' exceeds maximum length")

            min_value = field_info.get('min_value')
            if min_value is not None and value < min_value:
                raise BadRequest(f"Field '{field_name}' is below the minimum value")

            max_value = field_info.get('max_value')
            if max_value is not None and value > max_value:
                raise BadRequest(f"Field '{field_name}' exceeds the maximum value")

            custom_validator = field_info.get('validator')
            if custom_validator is not None:
                if not custom_validator(value):
                    raise BadRequest(f"Custom validation failed for field '{field_name}'")

    def process(self, data):
        formatted_data = self.format(data)
        self.validate(formatted_data)
        return formatted_data

    def add_field(self, field_name, field_info):
        self.fields[field_name] = field_info

    def remove_field(self, field_name):
        if field_name in self.fields:
            del self.fields[field_name]

    def set_default(self, field_name, default_value):
        if field_name in self.fields:
            self.fields[field_name]['default'] = default_value

    def set_required(self, field_name, required=True):
        if field_name in self.fields:
            self.fields[field_name]['required'] = required

    def set_nullable(self, field_name, nullable=True):
        if field_name in self.fields:
            self.fields[field_name]['nullable'] = nullable

    def set_type(self, field_name, field_type):
        if field_name in self.fields:
            self.fields[field_name]['type'] = field_type

    def set_choices(self, field_name, choices):
        if field_name in self.fields:
            self.fields[field_name]['choices'] = choices

    def set_max_length(self, field_name, max_length):
        if field_name in self.fields:
            self.fields[field_name]['max_length'] = max_length

    def set_min_value(self, field_name, min_value):
        if field_name in self.fields:
            self.fields[field_name]['min_value'] = min_value

    def set_max_value(self, field_name, max_value):
        if field_name in self.fields:
            self.fields[field_name]['max_value'] = max_value

    def set_validator(self, field_name, validator):
        if field_name in self.fields:
            self.fields[field_name]['validator'] = validator

    def rename_field(self, old_field_name, new_field_name):
        if old_field_name in self.fields:
            self.fields[new_field_name] = self.fields.pop(old_field_name)

    def hide_field(self, field_name):
        if field_name in self.fields:
            self.fields[field_name]['hidden'] = True

    def show_field(self, field_name):
        if field_name in self.fields:
            self.fields[field_name]['hidden'] = False

    def hide_fields(self, field_names):
        for field_name in field_names:
            self.hide_field(field_name)

    def show_fields(self, field_names):
        for field_name in field_names:
            self.show_field(field_name)

    def filter_fields(self, data):
        filtered_data = {}
        for field_name, field_info in self.fields.items():
            if not field_info.get('hidden', False) or field_name not in data:
                filtered_data[field_name] = data.get(field_name)
        return filtered_data
