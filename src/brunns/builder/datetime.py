# encoding=utf-8
import datetime
import logging

from brunns.builder import Builder, an_integer

logger = logging.getLogger(__name__)


class DateBuilder(Builder):
    target = datetime.date
    year = lambda: an_integer(1, 9999)
    month = lambda: an_integer(1, 12)
    day = lambda: an_integer(1, 28)
