# coding=utf-8
"""
Module of SqlFilters class.
"""

__author__ = 'https://github.com/akvilary'


from .constants import AND_MODE, OR_MODE
from .sql_filter import SqlFilter
from .abstracts.string_convertible import StringConvertible


class SqlFilters(StringConvertible):
    """
    SqlFilters class is invented to build sql filters faster.
    """

    def __init__(self, filters: dict, mode: str = AND_MODE):
        self.filters = filters
        self.mode = mode

    def __str__(self):
        converted = ''
        if self.filters:
            method = (
                '__rand__'  # converted & current_filter
                if self.mode.upper() == AND_MODE
                else '__ror__'  # converted | current_filter
                if self.mode.upper() == OR_MODE
                else None
            )
            if method:
                for key, value in self.filters.items():
                    current_filter = SqlFilter({key: value})
                    converted = getattr(current_filter, method)(converted)
        return converted
