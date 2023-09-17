__all__ = ['PrependingLoader']

from typing import List, Tuple, Callable
from jinja2 import BaseLoader, FileSystemLoader, Environment


class PrependingLoader(BaseLoader):
    """
    Usage:
    >>>loader = FileSystemLoader('')
    >>>env = Environment(loader=PrependingLoader(loader, 'some_macro.j2'))
    """

    # https://codyaray.com/2015/05/auto-load-jinja2-macros

    def __init__(self, delegate: BaseLoader, prepend_template_paths: List[str]):
        assert type(prepend_template_paths) == list, 'prepend_template_paths must be a list of strings'
        self.delegate = delegate
        self.prepend_template_paths = prepend_template_paths
        self.prepend_data: List[Tuple[str, Callable]] = []

    def get_source(self, environment, template: str):

        # Prepare templates
        for prepend_template_path in self.prepend_template_paths:
            prepend_source, _, prepend_uptodate = self.delegate.get_source(environment, prepend_template_path)
            self.prepend_data.append((prepend_source, prepend_uptodate))

        # main template
        main_source, main_filename, main_uptodate = self.delegate.get_source(environment, template)

        # upto_date
        final_source = "".join([tup[0] for tup in self.prepend_data]) + main_source
        final_uptodate = lambda: all(tup[1]() for tup in self.prepend_data) and main_uptodate()
        return final_source, main_filename, final_uptodate

    def list_templates(self):
        return self.delegate.list_templates()


