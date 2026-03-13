from src.parsers.base.parser_interface import ParserInterface


class BaseParser(ParserInterface):
    source_name: str

    def __init__(self):
        pass
