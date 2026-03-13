class ParserRegistry:
    _parsers = {}

    @classmethod
    def register(cls, source: str, parser) -> None:
        cls._parsers[source] = parser

    @classmethod
    def get_parser(cls, source: str) -> dict[str, str]:
        return cls._parsers[source]
