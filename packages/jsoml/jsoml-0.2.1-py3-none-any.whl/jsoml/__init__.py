from . import encoder, decoder
from lxml import etree

import io
from warnings import warn
from pathlib import Path


def dump(data, file):
    """
    Serialize data as JSOML XML to file (a pathlib.Path, file or file-like object).
    """

    if isinstance(file, str):
        raise ValueError("file must be file-like object or pathlib.Path")
    if isinstance(file, Path):
        file = str(file)
    if isinstance(file, io.TextIOBase):
        file = file.buffer
    tree = etree.ElementTree(encoder.xml_from_data(data))
    tree.write(file, encoding="utf-8", xml_declaration=True)


def dumps(data):
    buf = io.BytesIO()
    dump(data, buf)
    return buf.getvalue().decode("utf-8")


def load(source):
    """
    Deserialize JSOML XML from source.

    source can be a file, file-like object, or pathlib.Path.

    Return like json.load.
    """

    if isinstance(source, str):
        raise ValueError("file must be file-like object or pathlib.Path")
    if isinstance(source, Path):
        source = str(source)
    root = etree.parse(source).getroot()
    if "key" in root.attrib:
        warn("Root XML element should not have key attribute", SyntaxWarning)
    return decoder.data_from_xml(root)


def loads(text):
    return load(io.BytesIO(text.encode('utf-8')))
