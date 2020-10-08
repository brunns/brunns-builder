# encoding=utf-8
import logging
from datetime import date
from email.mime.text import MIMEText
from pathlib import Path

import pytest
from brunns.matchers.object import has_identical_properties_to
from brunns.matchers.smtp import email_with
from furl import furl
from hamcrest import assert_that, has_properties, instance_of, not_

from brunns.builder import Builder, a_boolean, a_string, an_integer, method
from brunns.builder.datetime import DateBuilder
from brunns.builder.email import EmailMessageBuilder
from brunns.builder.file import PathBuilder
from brunns.builder.internet import UrlBuilder

logger = logging.getLogger(__name__)


def test_builder_using_only_defaults():
    # Given
    class SomeClass:
        def __init__(self, a, b=None, c=None):
            self.a = a
            self.b = b
            self.c = c

    class SomeClassBuilder(Builder):
        target = SomeClass
        a = 4
        b = a_boolean

    builder = SomeClassBuilder()

    # When
    actual = builder.build()

    # Then
    assert_that(actual, instance_of(SomeClass))
    assert_that(actual, has_properties(a=4))


def test_building_using_positional_args():
    # Given
    class SomeClass:
        def __init__(self, a, b, c=None):
            self.a = a
            self.b = b
            self.c = c

    class SomeClassBuilder(Builder):
        target = SomeClass
        args = [1, lambda: 2]
        c = "sausages"

    builder = SomeClassBuilder()

    # When
    actual = builder.build()

    # Then
    assert_that(actual, instance_of(SomeClass))
    assert_that(actual, has_properties(a=1, b=2, c="sausages"))


def test_setting_values_by_with_method():
    # Given
    class SomeClass:
        def __init__(self, a, b, c=None):
            self.a = a
            self.b = b
            self.c = c

    class SomeClassBuilder(Builder):
        target = SomeClass
        a = 4
        b = a_string

    builder = SomeClassBuilder()

    # When
    actual = builder.with_a(99).build()

    # Then
    assert_that(actual, instance_of(SomeClass))
    assert_that(actual, has_properties(a=99))


def test_setting_values_by_and_method():
    # Given
    class SomeClass:
        def __init__(self, a, b):
            self.a = a
            self.b = b

    class SomeClassBuilder(Builder):
        target = SomeClass
        a = 4
        b = a_string

    builder = SomeClassBuilder()

    # When
    actual = builder.with_a(99).and_b("hello").build()

    # Then
    assert_that(actual, instance_of(SomeClass))
    assert_that(actual, has_properties(a=99, b="hello"))


def test_setting_values_by_kwargs():
    # Given
    class SomeClass:
        def __init__(self, a, b, c=None):
            self.a = a
            self.b = b
            self.c = c

    class SomeClassBuilder(Builder):
        target = SomeClass
        a = 4
        b = a_string

    # When
    actual = SomeClassBuilder(a=99).build()

    # Then
    assert_that(actual, instance_of(SomeClass))
    assert_that(actual, has_properties(a=99))


def test_values_and_factories():
    # Given
    class SomeClass:
        def __init__(self, a, b):
            self.a = a
            self.b = b

    class SomeClassBuilder(Builder):
        target = SomeClass
        a = 4
        b = lambda: "sausages"

    builder = SomeClassBuilder()

    # When
    actual = builder.build()

    # Then
    assert_that(actual, instance_of(SomeClass))
    assert_that(actual, has_properties(a=4, b="sausages"))


def test_multiple_builders_do_not_interfere():
    # Given
    class SomeClass:
        def __init__(self, a, b, c=None):
            self.a = a
            self.b = b
            self.c = c

    class SomeClassBuilder(Builder):
        target = SomeClass
        a = lambda: 4
        b = a_string

    builder1 = SomeClassBuilder()
    builder2 = SomeClassBuilder()

    # When
    actual1 = builder1.with_a(99).build()
    actual2 = builder2.build()

    # Then
    assert_that(actual1, not_(has_identical_properties_to(actual2)))


def test_url_builder():
    # Given
    builder = UrlBuilder()

    # When
    url1 = builder.build()
    url2 = builder.build()
    url3 = builder.with_host("example.com").build()
    url4 = UrlBuilder().build()

    # Then
    assert_that(url1, instance_of(furl))
    assert_that(url1, has_identical_properties_to(url2))
    assert_that(url1, not_(has_identical_properties_to(url3)))
    assert_that(url1, not_(has_identical_properties_to(url4)))


def test_date_builder():
    # Given
    builder = DateBuilder()

    # When
    actual = builder.build()

    # Then
    assert_that(actual, instance_of(date))


def test_path_builder():
    # Given
    builder = PathBuilder()

    # When
    actual = builder.build()

    # Then
    assert_that(actual, instance_of(Path))


def test_nested_builders():
    # Given
    builder = EmailMessageBuilder(subject="Chips are nice")

    # When
    actual = builder.with_to_name("simon").build()

    # Then
    assert_that(actual, instance_of(MIMEText))
    assert_that(actual.as_string(), email_with(to_name="simon", subject="Chips are nice"))


def test_additional_methods():
    # Given
    class MethodUsingBuilder(Builder):
        a = lambda: 4
        b = lambda: 7

        def build(self):
            return self.some_maths()

        @method
        def some_maths(self):
            return self.a + self.b

    # When
    actual = MethodUsingBuilder().build()

    # Then
    assert actual == 11


def test_neither_target_nor_build():
    # Given
    class BrokenBuilder(Builder):
        a = 4

    # When
    with pytest.raises(ValueError):
        BrokenBuilder().build()


def test_builder_as_object_proxy():  # noqa: C901
    # Given
    class SomeClass:
        def __init__(self, a, b):
            self.a = a
            self.b = b

        def mult(self):
            return self.a * self.b

        def __getitem__(self, item):
            return self.b

        def __repr__(self):
            return "test repr"

        def __str__(self):
            return "test str"

    class SomeClassBuilder(Builder):
        target = SomeClass
        a = an_integer
        b = an_integer

    builder = SomeClassBuilder(a=2, b=3)

    # When

    # Then
    assert_that(builder, instance_of(SomeClassBuilder))
    assert builder.mult() == 6
    assert builder["whatever"] == 3
    assert repr(builder) == "test repr"
    assert str(builder) == "test str"
