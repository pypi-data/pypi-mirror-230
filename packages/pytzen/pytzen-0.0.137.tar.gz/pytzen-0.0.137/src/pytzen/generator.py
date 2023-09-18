import os
import json
import textwrap
from abc import ABCMeta, abstractmethod
from pytzen.logs import Logger



class DocMeta(ABCMeta):


    @classmethod
    def find_file_name(cls):
        nb_files = [f for f in os.listdir('.') if f.endswith('.json')]
        if len(nb_files) == 1:
            file_name = nb_files[0].split('.')[0]
            return file_name
        else:
            raise ValueError('Please let one JSON in the folder.')
    

    @classmethod
    def get_class_pattern(cls, file_name):
        with open(f'{file_name}.json') as file:
            class_pattern = json.load(file)
        return class_pattern
    

    def generate_class_doc(self, width=68, indent=' '*4):

        doc_str = self.class_pattern['description'] + '\n\n'
        doc_str += 'Inputs:\n'
        for k, v in self.class_pattern['inputs'].items():
            line = f'- {k}: {v}'
            doc_str += textwrap.fill(line, width=width, 
                                     subsequent_indent=indent) + '\n'
        
        doc_str += '\nAttributes:\n'
        for k, v in self.class_pattern['attributes'].items():
            line = f'- {k}: {v}'
            doc_str += textwrap.fill(line, width=width, 
                                     subsequent_indent=indent) + '\n'
            
        doc_str += '\nMethods:\n'
        for k, v in self.class_pattern['methods'].items():
            line = f'- {k}: {v}'
            doc_str += textwrap.fill(line, width=width, 
                                     subsequent_indent=indent) + '\n'
        
        return doc_str


    def __new__(cls, name, bases, attrs):

        new_class = super(DocMeta, cls).__new__(cls, name, bases, attrs)
        new_class.file_name = cls.find_file_name()
        new_class.class_pattern = cls.get_class_pattern(new_class.file_name)
        new_class.__doc__ = new_class.generate_class_doc()

        return new_class



class ZenGenerator(metaclass=DocMeta):

    def __init__(self, log_level='INFO', **kwargs):

        self.logs = Logger(name=self.file_name, level=log_level)

        for input_name in self.class_pattern['inputs']:
            if input_name not in kwargs:
                raise ValueError(f'{input_name} must be provided!')
            setattr(self, input_name, kwargs[input_name])
        
        for attr_name in self.class_pattern['attributes']:
            setattr(self, attr_name, None)

        for method_name in self.class_pattern['methods']:
            vars()[method_name] = abstractmethod(lambda self: None)