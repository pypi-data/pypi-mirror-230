# `pytzen`
----

## Disclaimer:
This library is offered 'as-is' with **no official support, maintenance, or warranty**. Primarily, `pytzen` is an experimentation and learning platform, which may not be apt for production settings. Users are encouraged to delve into the library but should note that the developers won't actively address arising issues.

## Code Access:
The associated GitHub repository is private. Direct access to the source code's versioning or issue tracking is restricted. However, the source code is available on this page and in the **Download files** section:
- **Source Distribution**: `pytzen-*.tar.gz`
- **Built Distribution**: `pytzen-*-py3-none-any.whl`

## Usage Caution:
We are not liable for issues stemming from the library's usage in production environments. Users should extensively test and vet the library in a safe space before expansive implementation.

----

# `ZenGenerator`
Tailored for data scientists, the ZenGenerator addresses the specific demands of dynamic model applications within the Jupyter Notebook ecosystem. Here's what it offers:

- **Dynamic Class Creation**: With just a dictionary input detailing attributes, effortlessly generate and instantiate Python classes.
- **Auto-Documentation**: Each dynamically formed class comes with automated documentation, ensuring clarity and coherence.
- **Rapid Prototyping**: Experience unrestricted class definition, immediate model testing, and tweaks—all in real-time.
- **Config-Driven Design**: It caters to classes birthed from configuration details or external datasets.
- **System Extensions**: It's a boon for enriching prevailing systems via new class plugins or extensions.
- **Jupyter Export**: Seamlessly export your Jupyter Notebook with the newly created class as both source code and markdown, facilitating a smooth transition between coding and documentation.

In summary, ZenGenerator molds a wholly functional, auto-documented Python class within Jupyter Notebook, primed for swift deployment and dissemination.

## Usage

Take a look at the prototype below. After that, consider the [real use cases.](https://github.com/pytzen/zen)


```python
import sys
sys.path.append('/home/pytzen/lab/pytzen/src')
import inspect
from pytzen.generator import ZenGenerator
```


```python
class_pattern = {
    "description": "Docstring explaining the class.",
    "inputs": {
        "some_input": "Docstring explaining the input.",
        "another_input": "Docstring explaining another input."
    },
    "attributes": {
        "some_attribute": "Docstring explaining the attribute.",
        "another_attribute": "Docstring explaining another attribute."
    },
    "methods": {
        "some_method": "Docstring explaining the method.",
        "another_method": "Docstring explaining another method."
    }
}
zen = ZenGenerator(class_pattern)
```


```python
@zen.create_method()
def some_method(self):
    self.some_attribute = 'some_attribute'

@zen.create_method()
def another_method(self):
    self.another_attribute = 'another_attribute'

gen_class = zen.ClassPattern(some_input='some_input', 
                             another_input='another_input')
print(gen_class.__doc__)
```

    {'inputs': {'some_input': 'Docstring explaining the input.',
                'another_input': 'Docstring explaining another input.'},
     'attributes': {'some_attribute': 'Docstring explaining the '
                                      'attribute.',
                    'another_attribute': 'Docstring explaining another '
                                         'attribute.'},
     'methods': {'some_method': 'Docstring explaining the method.',
                 'another_method': 'Docstring explaining another '
                                   'method.'}}



```python
gen_class.some_method()
print(gen_class.status)
```

    some_input
    {'objects_missed': {'attributes': {'another_attribute': 'Docstring '
                                                            'explaining '
                                                            'another '
                                                            'attribute.'}}}



```python
gen_class.another_method()
```

    Class design is complete. New class exported.



```python
print(gen_class.status)
```

    Enjoy!


## Source Code

```python
from pprint import pformat
import os
import nbformat
from nbconvert import PythonExporter, MarkdownExporter
```


```python
print(inspect.getsource(ZenGenerator))
```

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
                        to_be_defined[class_item] = dict_item
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
    

