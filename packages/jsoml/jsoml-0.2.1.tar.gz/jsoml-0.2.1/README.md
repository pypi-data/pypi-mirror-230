JSOML
=====

JSOML (JavaScript Object Markup Language) is an XML format representing data structures
that can be serialized in JSON/YAML.  JSON/YAML can round-trip through JSOML
and vice-versa.

JSOML serializes large strings in a more readable and diff-friendly manner than JSON.
This is particularly useful for strings of HTML content (or other non-XML formats) that
are stored in data structures used with JSON.

Text (without the trigram `]]>`) can be included unmodified within JSOML (in a CDATA
section).

For example, a data structure serialized in JSON as:
```json
{
    "date": "2022-04-14",
    "authors": [
        {
            "given-names": "Begoña José",
            "surname": "Sagües",
        }
    ],
    "html": "<h1 id=\"title\">On Testing</h1>\n<h2 id=\"introduction\">Introduction</h2>\n<p>\nBegoña José Sagües\nis \"testing\".\n</p>\n",
}
```

is serialized in JSOML as:
```xml
<obj>
    <str key="date" val="2022-04-14"/>
    <arr key="authors">
        <obj>
            <str key="given-names" val="Begoña José"/>
            <str key="surname" val="Sagües"/>
        </obj>
    </arr>
    <str key="html"><notline/><![CDATA[
<h1 id="title">On Testing</h1>
<h2 id="introduction">Introduction</h2>
<p>
Begoña José Sagües
is "testing".
</p>
]]></str>
</obj>
```

This Python library provides methods `dump`, `load`, `dumps`, and `loads` for
reading and writing JSOML.  They behave similarly to the methods of the same name in the
`json` module of the Python standard library.


YAML vs JSOML
-------------

Unlike XML, YAML provides a lightweight format like JSON. Like JSOML, large strings can
be serialized in YAML in a more readable and diff-friendly manner.
However, YAML requires modification of strings in the form of indenting all lines or
escaping double quotes and newline characters.

In contrast, JSOML only requires the trigram `]]>` to be escaped. All other lines of a string
can be included unmodified. It is a trade-off between small modification of all lines of a string
with YAML vs large modification of the rare trigram `]]>` with JSOML.


Specification
-------------

JSOML is an XML format with a schema of eight XML elements.
Seven of these XML elements are the "*JSON XML elements*".
They correspond directly to the to seven JSON value tokens:

* `<obj>` for a JSON object
* `<arr>` for a JSON array
* `<num/>` for a JSON number
* `<str>` for a JSON string
* `<null/>` for JSON "null"
* `<true/>` for JSON "true"
* `<false/>` for JSON "false"

The eighth XML element is `<notline/>`. It only appears as a child element of `<str>`
and is the only XML element that `<str>` can contain. It modifies the semantics of the
XML character content of `<str>`. See below for more details.


### XML attribute `key=`

A JSOML XML element has a `key` attribute if and only if it is a child element of an
`<obj>` element. The string value is the corresponding key value in JSON.


### XML attribute `val=`

The `<num>` element must have a `val` attribute. Its value corresponds exactly
to the corresponding number token value in JSON.

An empty `<str/>` element may have a `val` attribute. It is an alternative to having the
string value as XML element content. Its string value corresponds to a string value in JSON.


### Considerations for `<str>` content

In the absence of any child `<notline/>` element of `<str>`, the XML contents
of `<str>` are processed as usual with XML. In particular, use of `<![CDATA[`
can be useful for including text unmodified until the trigram `]]>`.

The semantics of `<notline/>` is to remove a newline character that follows it.
Apart from this child element and a newline character that follows it,
all other character content contained by `<str>` is processed as usual with XML.

The combination of `<notline/>` and `<![CDATA[` together can be useful for
multiline strings as seen in the example above.
This combination is also useful for handling string values with the trigram `]]>`,
as shown in the example below. Consider a string value which in Python can be
coded as
```
"""Is the mathematical condition 
$$
E[x[i]]>0
$$
problematic?
"""
```

This Python string is encoded in JSON as:
```
"Is the mathematical condition\n$$\nE[x[i]]>0\n$$\nproblematic?\n"
```

and in JSOML it can be encoded as:
```
<str><notline/><![CDATA[
Is the mathematical condition
$$
E[x[i]]><notline/><![CDATA[
]]&gt;<notline/><![CDATA[
0
$$
problematic?
]]></str>
```

This escaping for JSOML can be achieved in code by replacing all substrings:
```
"]]>"
```
with the substring:
```
"]]><notline/><![CDATA[\n]]&gt;<notline/><![CDATA[\n"
```
