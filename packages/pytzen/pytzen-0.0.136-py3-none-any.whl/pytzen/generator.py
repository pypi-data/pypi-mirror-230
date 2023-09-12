from pprint import pformat
import os
import nbformat
from nbconvert import PythonExporter, MarkdownExporter

class ZenGenerator:
    def __init__(self, class_pattern: dict):
        self.class_pattern = class_pattern
        self.file_name = self.find_file_name()
        self.ClassPattern = self.create_class()
        self.ClassPattern.defined_objects = []
        self.ClassPattern.status = {}
        self.ClassPattern.__doc__ = self.check_status(is_doc=True)
    
    def check_status(self, is_doc=False):
        to_be_defined = {}
        for class_item, obj_dict in self.class_pattern.items():
            if class_item != 'description':
                dict_item = {}
                for obj in obj_dict:
                    if obj not in self.ClassPattern.defined_objects:
                        dict_item[obj] = obj_dict[obj]
                if dict_item:
                    if is_doc:
                        to_be_defined[class_item] = dict_item
                    else:
                        to_be_defined[class_item] = list(dict_item.keys())
        status = {'objects_missed': to_be_defined}
        if is_doc:
            status = to_be_defined
        if to_be_defined:
            doc = pformat(status, width=68, sort_dicts=False)
        else:
            doc = 'Enjoy!'
            self.export_class()
        return doc

    def find_file_name(self, directory='.'):
        nb_files = [f for f in os.listdir(directory) if f.endswith('.ipynb')]
        if len(nb_files) == 1:
            return nb_files[0].split('.')[0]
        else:
            raise ValueError('Please let one saved notebook in the folder.')

    def create_class(self):
        inputs = self.class_pattern['inputs']
        class ClassPattern:
            def __init__(self, **kwargs):
                for input_attribute in kwargs:
                    if input_attribute in inputs:
                        setattr(self, input_attribute, kwargs[input_attribute])
                        self.defined_objects.append(input_attribute)
        return ClassPattern

    def create_method(self):
        check_status = self.check_status
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                result = func(self, *args, **kwargs)
                new_attributes = list(self.__dict__.keys())
                self.defined_objects.extend(new_attributes)
                self.status = check_status()
                return result
            setattr(self.ClassPattern, func.__name__, wrapper)
            self.ClassPattern.defined_objects.append(func.__name__)
            return wrapper
        return decorator

    def export_class(self):
        notebook_name = f'{self.file_name}.ipynb'
        def export_to_format(exporter, output_path):
            body, _ = exporter.from_notebook_node(
                nbformat.read(notebook_name, as_version=4))
            with open(output_path, 'w') as f:
                f.write(body)
        path_md = os.path.join(os.getcwd(), 'README.md')
        exporter = MarkdownExporter()
        export_to_format(exporter, path_md)
        path_py = os.path.join(os.getcwd(), f'{self.file_name}.py')
        exporter = PythonExporter()
        export_to_format(exporter, path_py)
        with open(path_py, 'r') as file:
            file_contents = file.read()
            file_contents = file_contents.replace('zen.export_class()', '')
        with open(path_py, 'w') as file:
            file.write(file_contents)
        print('Class design is complete. New class exported.')