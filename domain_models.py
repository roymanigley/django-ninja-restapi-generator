import datetime
import random
import re
import string
from typing import List


class DomainModelField(object):

    def __init__(self, name:str, type='str', required=True, max_len=None):
        self.name = name
        self.class_type = type
        self.class_type_snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', self.name).lower()
        self.class_type_kebab_case = re.sub(r'(?<!^)(?=[A-Z])', '-', self.name).lower()
        self.required = required
        self.max_len = max_len

    def to_django_model_field(self) -> str:
        django_model_field = f'{self.name} = models.'
        if self.class_type == 'str' and self.max_len:
            django_model_field += f'CharField(max_length={self.max_len}, null={not self.required})'
        elif self.class_type == 'str' and self.max_len is None:
            django_model_field += f'TextField(null={not self.required})'
        elif self.class_type == 'int':
            django_model_field += f'IntegerField(null={not self.required})'
        elif self.class_type == 'float':
            django_model_field += f'FloatField(null={not self.required})'
        elif self.class_type == 'date':
            django_model_field += f'DateField(null={not self.required})'
        elif self.class_type == 'datetime':
            django_model_field += f'DateTimeField(null={not self.required})'
        elif self.class_type.startswith('enum'):
            django_model_field += f'CharField(max_length={self.max_len if self.max_len else 100}, choices={self.class_type.replace("enum.", "")}.choices, null={not self.required})'
        else:
            django_model_field += f'ForeignKey({self.class_type}, on_delete=models.DO_NOTHING, null={not self.required})'
        return django_model_field

    def is_fk(self):
        return not self.class_type in ['str', 'int', 'float', 'date', 'datetime'] and not self.class_type.startswith('enum.')

    def to_django_ninja_schema_in_field(self):
        class_type = self.class_type
        name = self.name
        if self.is_fk():
            class_type = f'int'
            name = f'{self.name}_id'
        if not self.required:
            class_type = f'Optional[{class_type}]'
        return f'{name}: {class_type.replace("enum.", "")}'

    def to_django_ninja_schema_out_field(self):
        class_type = self.class_type
        if self.is_fk():
            class_type = f'{class_type}SchemaOut'
        if not self.required:
            class_type = f'Optional[{class_type}]'
        return f'{self.name}: {class_type.replace("enum.", "")}'

    def to_django_ninja_schema_field_all_optional(self):
        class_type = self.class_type
        name = self.name
        if self.is_fk():
            class_type = f'int'
            name = f'{self.name}_id'
        return f'{name}: Optional[{class_type.replace("enum.", "")}]'


class DomainEnum(object):

    def __init__(self, name: str, values: List[str]):
        self.name = name
        self.values = values
        self.name_snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', self.name).lower()
        self.name_kebab_case = re.sub(r'(?<!^)(?=[A-Z])', '-', self.name).lower()

    def to_django_model_enum(self) -> str:
        django_model_enum = f'class {self.name}(models.TextChoices):\n'
        for value in self.values:
            django_model_enum += f'    {value} = (\'{value}\', \'{value}\')\n'
        return django_model_enum + '\n\n'


class DomainModel(object):

    def __init__(self, name: str, fields: List[DomainModelField]):
        self.name = name
        self.name_snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', self.name).lower()
        self.name_kebab_case = re.sub(r'(?<!^)(?=[A-Z])', '-', self.name).lower()
        self.fields = fields

    def to_django_model(self) -> str:
        django_model = f'class {self.name}(models.Model):\n'
        for field in self.fields:
            django_model += f'    {field.to_django_model_field()}\n'

        django_model += '    creator = models.CharField(max_length=255, blank=False)\n'
        django_model += '    create_date = models.DateTimeField(blank=False)\n'
        django_model += '    modifier = models.CharField(max_length=255, blank=False)\n'
        django_model += '    modified_date = models.DateTimeField(blank=False)\n'
        return django_model + '\n\n'

    def to_django_ninja_schema(self) -> str:
        django_model = f'class {self.name}SchemaIn(Schema):\n'
        for field in self.fields:
            django_model += f'    {field.to_django_ninja_schema_in_field()}\n'

        django_model += f'\n\nclass {self.name}SchemaInPatch(Schema):\n'
        for field in self.fields:
            django_model += f'    {field.to_django_ninja_schema_field_all_optional()}\n'

        django_model += f'\n\nclass {self.name}SchemaOut(Schema):\n'
        django_model += '    id: int\n'
        for field in self.fields:
            django_model += f'    {field.to_django_ninja_schema_out_field()}\n'
        django_model += '    creator: str\n'
        django_model += '    create_date: datetime\n'
        django_model += '    modifier: str\n'
        django_model += '    modified_date: datetime\n'
        return django_model + '\n\n'

    def to_django_ninja_filter_schema(self) -> str:
        django_model = f'class {self.name}FilterSchema(FilterSchema):\n'
        for field in self.fields:
            if field.class_type == 'str':
                django_model += f'    {field.name}: Optional[{field.class_type.replace("enum.", "")}] = Field(q="{field.name}__icontains")'
            elif field.class_type in ['int', 'float', 'date', 'date_time'] or field.class_type.startswith('enum.'):
                django_model += f'    {field.name}: Optional[{field.class_type.replace("enum.", "")}]'
            else:
                django_model += f'    {field.name}_id: Optional[int]'
            django_model += '\n'

        django_model += '    creator: Optional[str] = Field(q="creator__icontains")\n'
        django_model += '    create_date: Optional[datetime]\n'
        django_model += '    modifier: Optional[str] = Field(q="modifier__icontains")\n'
        django_model += '    modified_date: Optional[datetime]\n'
        return django_model + '\n\n'

    def create_valid_dictionary_entries_for_update_test(self) -> str:
        return self.create_valid_dictionary_entries_for_tests().replace('.values[0]', '.values[1]')

    def create_valid_dictionary_entries_for_tests(self) -> str:
        dictionary_entries = ''
        for field in self.fields:
            if field.required:
                if field.class_type == 'str':
                    value = '"' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=field.max_len if field.max_len is not None else 1024)) + '"'
                    dictionary_entries += f'"{field.name}": {value}'
                elif field.class_type == 'int':
                    value = random.randint(1, 200)
                    dictionary_entries += f'"{field.name}": {value}'
                elif field.class_type == 'float':
                    value = random.random()
                    dictionary_entries += f'"{field.name}": {value}'
                elif field.class_type == 'date':
                    today = datetime.date.today()
                    value = datetime.date.fromordinal(random.randint(today.toordinal() - 1000, today.toordinal())).isoformat()
                    dictionary_entries += f'"{field.name}": datetime.date.fromisoformat("{value}")'
                elif field.class_type == 'datetime':
                    now = datetime.datetime.now()
                    value = datetime.datetime.fromordinal(random.randint(now.toordinal() - 1000, now.toordinal())).isoformat()
                    dictionary_entries += f'"{field.name}": datetime.datetime.fromisoformat("{value}")'
                elif field.class_type.startswith('enum.'):
                    dictionary_entries += f'"{field.name}": {field.class_type.replace("enum.", "")}.values[0]'
                else:
                    dictionary_entries += f'"{field.name}_id": {field.class_type}RestTest.create_persisted()["id"]'
            else:
                if field.class_type in ['str', 'int', 'float', 'date', 'datetime'] or field.class_type.startswith('emum.'):
                    dictionary_entries += f'"{field.name}": None'
                else:
                    dictionary_entries += f'"{field.name}_id": None'
            dictionary_entries += ',\n            '
        return dictionary_entries

    def create_invalid_dictionary_entries_for_tests(self) -> str or None:
        dictionary_entries = ''
        for field in self.fields:
            if field.required:
                dictionary_entries += f'"{field.name}": None,\n'
        return dictionary_entries

    def create_assertion_for_tests(self) -> str:
        assertions = ''
        for field in self.fields:
            if field.class_type in ['str', 'int', 'float'] or field.class_type.startswith('enum.'):
                assertions += f'self.assertEqual(actual["{field.name}"], expected["{field.name}"])\n        '
            elif field.class_type in ['date', 'datetime']:
                assertions += f'self.assertEqual(actual["{field.name}"], expected["{field.name}"].isoformat())\n        '
            else:
                assertions += f'self.assertEqual(actual["{field.name}"]["id"], expected["{field.name}_id"])\n        '
        return assertions


class DomainModels(object):

    def __init__(self, app_name: str, entities: List[DomainModel], enums: List[DomainEnum]=None):
        self.app_name = app_name
        self.app_name_snake_case = app_name.replace('-', '_').replace(' ', '_').lower()
        self.entities = entities
        self.domain_enums = enums if enums is not None else []

    def to_django_models(self) -> str:
        django_models = 'from django.db import models\n\n'
        for enum in self.domain_enums:
            django_models += enum.to_django_model_enum()
        for entity in self.entities:
            django_models += entity.to_django_model()
        return django_models
