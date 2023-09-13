import abc
import re

import mistune
import markdownify
import nh3
from bs4 import BeautifulSoup
from bs4.diagnose import diagnose


def _standardize_block_math(math_input: re.Match):
    math_content = math_input.group(1)
    if math_content:
        clean_math_text = math_content.strip()
        return f'\n$$\n{clean_math_text}\n$$\n'
    return math_input.group()


class BaseContentStage(abc.ABC):

    @abc.abstractmethod
    def validate_input(self):
        pass

    @abc.abstractmethod
    def sanitize(self, raise_exception: bool = False):
        pass

    @abc.abstractmethod
    def apply(self, raise_exception: bool = False):
        pass


class HTML2MDContentStage(BaseContentStage):

    def __init__(self, content: str):
        self.content = content

    def validate_input(self):
        return nh3.is_html(self.content)
        # soup = BeautifulSoup(self.content, 'lxml')
        # report = diagnose(soup)
        # if not report:
        #     return True
        # else:
        #     return False

    def sanitize(self, raise_exception: bool = False):
        pass

    def apply(self, raise_exception: bool = False):
        is_valid_html = self.validate_input()
        if not is_valid_html:
            if raise_exception:
                raise
            else:
                return ''

        math_escaped_patterns = [
            (r'\\\((.*?)\\\)',  r'\\\(\1\\\)'),
            (r'\\\[(.*?)\\\]', _standardize_block_math),
            (r'\$\$(.*?)\$\$', _standardize_block_math),
        ]
        escaped_content = markdownify.markdownify(self.content)
        for r1, r2 in math_escaped_patterns:
            escaped_content = re.sub(r1, r2, escaped_content)
        result = re.sub(r'\$\$\n(.*?)\n\$\$', r'$$\1$$', escaped_content)
        return result


class MD2HTMLContentStage(BaseContentStage):

    def __init__(self, content: str):
        self.content = content

    def validate_input(self):
        return True

    def sanitize(self, raise_exception: bool = False):
        pass

    def apply(self, raise_exception: bool = False):
        is_valid_md = self.validate_input()
        if not is_valid_md:
            if raise_exception:
                raise
            else:
                return ''
        html_parser = mistune.create_markdown(
            escape=False,
            plugins=['strikethrough', 'footnotes', 'table', 'speedup', 'url', 'math', 'superscript', 'subscript']
        )
        math_escaped_patterns = [
            (r'\\\((.*?)\\\)',  r'\\\(\1\\\)'),
            (r'\\\[(.*?)\\\]', _standardize_block_math),
            (r'\$\$(.*?)\$\$', _standardize_block_math),
        ]
        escaped_content = self.content
        for r1, r2 in math_escaped_patterns:
            escaped_content = re.sub(r1, r2, escaped_content)
        result = html_parser(escaped_content)
        result = re.sub(r'\$\$\n(.*?)\n\$\$', r'$$\1$$', result)
        return result
