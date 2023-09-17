from __future__ import annotations

from skoufas_dbf_reader.correction_data import converted_entries
from skoufas_dbf_reader.utilities import all_entries, none_if_empty_or_stripped, read_yaml_data, romanize


def test_yaml_data():
    no_author = read_yaml_data("language_codes")
    assert no_author
    assert type(no_author) == dict
    assert len(no_author) > 0


def test_none_if_empty_or_stripped():
    assert none_if_empty_or_stripped(None) is None
    assert none_if_empty_or_stripped("") is None
    assert none_if_empty_or_stripped(" ") is None
    assert none_if_empty_or_stripped("   ") is None
    assert none_if_empty_or_stripped("foo") == "foo"
    assert none_if_empty_or_stripped("    foo ") == "foo"


def test_all_entries():
    entries = all_entries()
    assert entries
    assert type(entries) == list
    assert len(entries) > 0
    entry = entries[0]
    assert type(entry) == dict
    assert entry[0] == 1

    assert entries[1000][0] == 1001


def test_converted_entries():
    all = converted_entries()
    assert all


def test_romanize():
    assert romanize("Γειά") == "Geia"
    assert romanize("") == ""
    assert romanize(None) == ""
