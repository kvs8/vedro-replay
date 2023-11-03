from typing import List

from pyparsing import CharsNotIn, Optional, Suppress, ZeroOrMore, restOfLine

from .exclude import Exclude


class ExcludeParser:
    path_part = CharsNotIn(".:").set_name("path part (any character except '.', ':')")

    path_part_separator = Suppress(".").set_name("separator between path parts (denoted as '.')")

    parts_path = (path_part + ZeroOrMore(path_part_separator + path_part))("parts_path").set_name(
        "the parts path to delete or change the value using a regular expression (for example 'result.id')"
    )

    paths_separator = Suppress(":").set_name("separator between path and regular expression (denoted as ':')")

    regular_expression = restOfLine("reg_exp").set_name("regular expression")

    exclude = (
        parts_path + Optional(paths_separator + regular_expression)
    ).set_name("exclude").set_parse_action(lambda t: {'parts_path': t.parts_path.asList(), 'reg_exp': t.reg_exp})

    @classmethod
    def parse(cls, data: str) -> Exclude:
        return Exclude(**cls.exclude.parse_string(data)[0])


def parse_excludes(raw_excludes: List[str]) -> List[Exclude]:
    return [ExcludeParser.parse(raw_exclude) for raw_exclude in raw_excludes]
