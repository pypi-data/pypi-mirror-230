import pytest

import jsoml

import os
from pathlib import Path


TESTS_DIR = Path(__file__).parent


def test_xml_int():
    got = jsoml.loads("<num val='1'/>")
    assert type(got) == int
    assert got == 1


def test_xml_int_float():
    got = jsoml.loads("<num val='1.0'/>")
    assert type(got) == float
    assert got == 1


test_cases = [
    (None, "<null/>"),
    (False, "<false/>"),
    (True, "<true/>"),
    (123, "<num val='123'/>"),
    (1.23, "<num val='1.23'/>"),
    ([], "<arr></arr>"),
    ({}, "<obj></obj>"),
    ("hi", "<str><![CDATA[hi]]></str>"),
    ("¡José!", "<str val='¡José!'/>"),
    ("¡José!", "<str><![CDATA[¡José!]]></str>"),
    ([True], "<arr> <true/> </arr>"),
    ({"a": None}, "<obj> <null key='a'/> </obj>"),
    (
        ["hi", "bye"],
        "<arr><str val='hi'/><str val='bye'/></arr>",
    ),
    (
        dict(foo="hi", bar="bye"),
        "<obj><str key='foo' val='hi'/><str key='bar' val='bye'/></obj>",
    ),
    ("\na\nb", "<str>\na\nb</str>"),
    ("a\nb", "<str><notline/>\na\nb</str>"),
    ("]]>", "<str>]]&gt;</str>"),
    ("a]]>", "<str>a]]&gt;</str>"),
    ("]]>b", "<str>]]&gt;b</str>"),
    ("a]]>b", "<str>a]]&gt;b</str>"),
]


@pytest.mark.parametrize("case", test_cases)
def test_xml_load(case):
    got = jsoml.loads(case[1])
    assert got == case[0]


@pytest.mark.parametrize("case", test_cases)
def test_xml_dumps_n_loads(case):
    expected = case[0]
    s = jsoml.dumps(expected)
    assert type(s) == str
    got = jsoml.loads(s)
    assert got == expected


@pytest.mark.parametrize("case", test_cases)
def test_xml_dump_n_load_file(case, tmp_path):
    expected = case[0]
    jsoml.dump(expected, tmp_path / "temp.xml")
    got = jsoml.load(tmp_path / "temp.xml")
    assert got == expected


syntax_error_cases = [
    "<root/>",
    "<str> <foo/> </str>",
    "<obj> <null/> </obj>",
    "<notline> <null/> </notline>",
]


@pytest.mark.parametrize("case", syntax_error_cases)
def test_xml_error(case):
    with pytest.raises(SyntaxError):
        jsoml.loads(case)


syntax_warn_cases = [
    "<obj key='root'/>",
    "<arr> <null key='why'/> </arr>",
    "<arr> No point <null/> point </arr>",
    "<arr> <null/> fishy </arr>",
    "<str> <notline/> </str>",
]


@pytest.mark.parametrize("case", syntax_warn_cases)
def test_xml_warn(case):
    with pytest.warns(SyntaxWarning):
        jsoml.loads(case)
