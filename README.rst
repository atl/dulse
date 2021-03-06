=============
    Dulse   
=============

| Dumb, but light & simple module for the extensible markup language.
| Dicts, unicode & lists seem enough.

Dulse is a module for when XML is probably too sophisticated a format, but you're using it anyway. 
Dulse is lossy with respect to the XML specification, but its compromises are designed to simplify access by using a small repertoire of native Python datatypes: dicts, unicode, lists, and (optionally) floats and ints. 
In this respect, it draws heavily from JSON for its inspiration.

Un-features
-----------

It's generally poor policy to define something in terms of what it is not. 
However, because XML parsers are well-known and well-represented in Python, it is instructive here to list what differs from the usual list of features in an XML parser.

Dulse does not support XML attributes. 
    They don't fit into the simple model. 
    If XML attributes are important to you, then you should go elsewhere.
Dulse is non-uniform. 
    XML elements are instantiated as dicts, strings, or numeric types throughout, depending on their content. 
    Collections of elements may appear as dicts, lists, or atomic types, again, depending on context.
Dulse does not respect document order throughout. 
    Because it uses dicts as the basic storage unit, mapping element name to element content, key ordering is arbitrary. 
    However, because sibling elements that share the same name are placed into a list, their relative order with respect to their mutual parent element is preserved.
Dulse begrudgingly supports mixed content
    It unmarshalls the whole span of mixed content as a string type by default.
Dulse neither preserves nor cares about the root element.
    (But the XML writer requires the name of the root element's tag.)
Dulse is unapologetically lossy. 
    Besides the ordering and attribute simplifications, it strips whitespace and ignores comments. 
    You are highly unlikely to be able to reproduce the input from the output.


Parser customization
--------------------

By default, Dulse's parser tries to be as clever and sensitive as possible about the underlying content, including checking for mixed content and converting to numeric types as aggressively as possible. 
If you know more about the underlying content model, you can turn off features as desired, sometimes resulting in a significant performance gain. 
For example, if you know there's no mixed content, you can instantiate a parser that doesn't constantly check for it::

    import dulse
    p = dulse.Parser(mixed_content=False)
    d = p.parse("hamlet.xml")

If you know ahead of time which elements are expected to contain mixed content, then you can sidestep the expensive blind checking and explicitly parse accounting for the mixed content elements::

    d = dulse.parse("hamlet.xml", mixed_elements=['LINE'])

Similarly, if you don't need to convert to numeric types, you can use one of the provided conversion functions, ``NUMBER_OR_COLLAPSE`` (default), ``NUMBER``, ``COLLAPSE_WHITESPACE``, ``STRING``, or ``NO_CONVERSION``::

    d = dulse.parse("hamlet.xml", conversion=dulse.STRING)

Alternatively, you can convert each value using a function of your devising, and passing it into the conversion option of dulse.Parser().

XML out
-------

A complementary XML serializer is also available. 
``dulse.to_xml(obj)`` will build a string from an atomic object or dict, and ``dulse.write(obj, file)`` will write to a filename or file handle. 
The name of the root element can be customized with the keyword argument ``root``, and the encoding of the output can be adjusted with the ``encoding`` keyword.

History & approach
------------------

Dulse began as an exercise in the pulldom and in trying to unify access between different textual encodings. 
The unifying project fell by the wayside, but I revisited the code for another project that -- had I chosen the data carrier format -- might have used JSON, but used XML instead. 
The basic design worked well, but then I did some basic speed profiling, and discovered that although it was simple, the approach using the pulldom wasn't necessarily as fast as expected. 
After reworking the code to use ElementTree, the module was ready to be let out into the wild.

This exists as released code because I couldn't easily find an equivalent myself when I've looked (there seem to be a few similar ActiveState recipes, though).
It's released as open source so that it might be easier for *me* to find it later.

License
-------

Dulse uses the MIT License.
