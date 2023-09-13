import json
from warnings import warn


def data_from_xml(element):
    do_whitespace_check = True
    if element.tag == "null":
        ret = None
    elif element.tag == "false":
        ret = False
    elif element.tag == "true":
        ret = True
    elif element.tag == "num":
        ret = json.loads(element.get("val"))
    elif element.tag == "arr":
        ret = list()
        for sub in element:
            ret.append(data_from_xml(sub))
            if "key" in sub.attrib:
                msg = "JSOML array subelement '{}' should not have key attribute"
                warn(msg.format(sub.tag), SyntaxWarning)
    elif element.tag == "obj":
        ret = dict()
        for sub in element:
            key = sub.get("key")
            if key is None:
                msg = "XML element with tag '{}' missing key attribute"
                raise SyntaxError(msg.format(sub.tag))
            ret[key] = data_from_xml(sub)
    elif element.tag == "str":
        ret = element.get("val")
        if ret is None:
            ret = element.text or ""
            for sub in element:
                if sub.tag != 'notline':
                    msg = "JSOML str children elements can only be notline elements"
                    raise SyntaxError(msg)
                if len(sub):
                    msg = "JSOML notline elements must be empty"
                    raise SyntaxError(msg)
                more = sub.tail or ""
                if more.startswith("\n"):
                    more = more[1:]
                else:
                    warn("Newline should follow notline element", SyntaxWarning)
                ret += more
            do_whitespace_check = False
    else:
        msg = "Unsupported XML element tag name '{}'"
        raise SyntaxError(msg.format(element.tag))
    if do_whitespace_check:
        check_whitespace(element)

    return ret


WSPACE_ERR_MSG = (
    "Only whitespace may appear around sub-elements inside XML of a list or dict"
)


def check_whitespace(element):
    if element.text and element.text.strip():
        warn(WSPACE_ERR_MSG, SyntaxWarning)
    for sub in element:
        if sub.tail and sub.tail.strip():
            warn(WSPACE_ERR_MSG, SyntaxWarning)
