from lxml import etree

import json
from warnings import warn

def xml_from_data(src_data):
    ret = etree.Element(xml_tag_for(src_data))
    assign_data_to_xml(ret, src_data)
    return ret


def xml_tag_for(src_data):
    if src_data is None:
        return "null"
    if src_data is False:
        return "false"
    if src_data is True:
        return "true"
    if isinstance(src_data, (int, float)):
        return "num"
    if isinstance(src_data, list):
        return "arr"
    if isinstance(src_data, dict):
        return "obj"
    return "str"


def assign_data_to_xml(ret, src_data, level=0, tab= "    "):
    assert len(tab.strip(" \t")) == 0
    newline = "\n" + tab * level
    child = None

    if ret.tag == "num":
        ret.attrib["val"] = json.dumps(src_data)
    elif ret.tag == "arr":
        for item in src_data:
            child = etree.Element(xml_tag_for(item))
            assign_data_to_xml(child, item, level + 1, tab)
            child.tail = newline + tab
            ret.append(child)
    elif ret.tag == "obj":
        for ikey, item in sorted(src_data.items()):
            child = etree.Element(xml_tag_for(item))
            child.attrib["key"] = str(ikey)
            assign_data_to_xml(child, item, level + 1, tab)
            child.tail = newline + tab
            ret.append(child)
            if not isinstance(ikey, str):
                warn("dict item key is not of type str", RuntimeWarning)
    elif ret.tag == "str":
        text = str(src_data)
        if "\n" in text or "]]>" in text:
            start = True
            for frag in text.split("]]>"):
                if not start:
                    notline = etree.Element("notline")
                    ret.append(notline)
                    notline.tail = "\n]]>"
                notline = etree.Element("notline")
                ret.append(notline)
                notline.tail = etree.CDATA("\n" + frag)
                start = False
        elif nice_xml_attribute(text):
            ret.attrib["val"] = text
        else:
            ret.text = etree.CDATA(text)

    if child is not None:
        # there are children elements so put start tag on its own line
        ret.text = newline + tab
        # need to reduce indent for last child
        child.tail = newline

    return ret


def nice_xml_attribute(text):
    temp = etree.Element("a")
    temp.attrib["val"] = text
    raw = etree.tostring(temp, encoding="utf-8").decode("utf-8")
    return (raw == f"""<a val="{text}"/>""")
