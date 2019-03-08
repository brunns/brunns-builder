# encoding=utf-8
import logging
from pathlib import Path

from brunns.builder import Builder, a_string

logger = logging.getLogger(__name__)


class PathBuilder(Builder):
    target = Path
    args = lambda: [a_string(), a_string()]
