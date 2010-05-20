try:
    from xml.etree import cElementTree as etree
except ImportError:
    from xml.etree import ElementTree as etree
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def none_strip(s):
    if s:
        return s.strip()
    else:
        return None

def addtodict(dictionary, key, value):
    if key not in dictionary:
        dictionary[key] = value
    else:
        if not isinstance(dictionary[key], list):
            dictionary[key] = [dictionary[key], value]
        else:
            dictionary[key].append(value)

def NUMBER_OR_COLLAPSE(string):
    try:
        return int(string)
    except (ValueError, TypeError):
        try:
            return float(string)
        except (ValueError, TypeError):
            if string:
                return " ".join(string.split()) or None
            else:
                return None

def NUMBER(string):
    try:
        return int(string)
    except (ValueError, TypeError):
        try:
            return float(string)
        except (ValueError, TypeError):
            if string:
                return string.strip() or None
            else:
                return None

def COLLAPSE_WHITESPACE(string):
    try:
        return " ".join(string.split())
    except AttributeError:
        return None

def STRING(string):
    try:
        return string.strip()
    except AttributeError:
        return None

NO_CONVERSION = lambda x: x

class SimpleXMLParser(object):
    """
    Simple XML parser class that completely disregards attributes, and
    mostly disregards order. Text nodes are returned as strings, elements
    are returned as dict entries. By default, elements with mixed content
    are automatically detected and are returned as a string of their contents.
    
    Multiple sibling elements with the same name append their content to a
    list containing all of their previous siblings' content. In this way,
    siblings with the same node name have their order retained among 
    themselves, but other items have indeterminate order, as with all dicts.
    
    This is intended to exist after a transform into the simple content form,
    yielding as compact a form for data as possible.
    
    For example, the following xml::
        <node>
            <title>My Book</title>
            <author>Me</author>
            <date>23 April 2009</date>
            <content><h1>Chapter 1</h1><p><em>These</em> are the times that
                try mens' soles....</p></content>
            <endnote>This is the first.</endnote>
            <endnote>This is the last.</endnote>
        </node>
    
    is parsed with::
        p = SimpleXMLParser()
        p.parse(file("sample.xml"))
        
    and results in::
        {'author': 'Me',
         'content': {'h1': 'Chapter 1',
                     'p': "<em>These</em> are the times that\n      try mens' soles...."},
         'date': '23 April 2009',
         'endnote': ['This is the first.', 'This is the last.'],
         'title': 'My Book'}
    
    This might not be the ideal form for your uses. If so, then you can change
    the way mixed content is handled and the way elements are converted::
    
        parse("sample.xml", conversion=COLLAPSE_WHITESPACE, mixed_elements=['content'])
    
    resulting in::
        {'author': 'Me',
         'content': "<h1>Chapter 1</h1><p><em>These</em> are the times that try mens' soles....</p>",
         'date': '23 April 2009',
         'endnote': ['This is the first.', 'This is the last.'],
         'title': 'My Book'}
    
    """
    def __init__(self, conversion=None, mixed_content=True, mixed_elements=None):
        self.events = None
        if conversion:
            self.conversion = conversion
        else:
            self.conversion = NUMBER_OR_COLLAPSE
        if not mixed_content:
            self.is_mixed = lambda x: False
        if mixed_elements:
            self.is_mixed = lambda x: x.tag in mixed_elements
    
    @staticmethod
    def is_mixed(ele):
        return bool((none_strip(ele.text) and ele.getchildren()) or 
            any(map(lambda x: none_strip(x.tail), ele.getchildren())))
    
    def get_mixed(self, z):
        if z.text:
            y = z.text + ''.join(map(etree.tostring, z.getchildren()))
        else:
            y = ''.join(map(etree.tostring, z.getchildren()))
        return self.conversion(y)
    
    def get_simple_xml_content(self, parentnode):
        d = {}
        for event, currnode in self.events:
            if event == 'start':
                addtodict(d, currnode.tag, self.get_simple_xml_content(currnode))
            elif event == 'end' and currnode == parentnode and self.is_mixed(currnode):
                return self.get_mixed(currnode)
            elif event == 'end' and currnode == parentnode:
                return d or self.conversion(currnode.text)
            else:
                print "unexpected branch"
                return self.conversion(currnode.text)
    
    def _parse(self):
        depth = 0
        d = {}
        for event, node in self.events:
            if (event == 'start') and (depth == 0):
                depth += 1
            elif event == 'end' and self.is_mixed(node):
                return self.get_mixed(node)
            elif event == 'end':
                depth -= 1
                if depth > 1:
                    addtodict(d, node.tag, self.conversion(node.text))
                elif not d:
                    d = self.conversion(node.text)
            elif event == 'start':
                addtodict(d, node.tag, self.get_simple_xml_content(node))
        return d
    
    def parse(self, stream_or_string):
        if isinstance(stream_or_string, basestring):
            stream = open(stream_or_string)
        else:
            stream = stream_or_string
        self.events = iter(etree.iterparse(stream, ('start', 'end')))
        d = self._parse()
        stream.close()
        return d
    
    def parse_string(self, string):
        bufsize = len(string)
        buf = StringIO(string)
        self.events = iter(etree.iterparse(buf, ('start', 'end')))
        d = self._parse()
        buf.close()
        return d

def parse(stream_or_string, **kwargs):
    p = SimpleXMLParser(**kwargs)
    return p.parse(stream_or_string)

def parse_string(string, **kwargs):
    p = SimpleXMLParser(**kwargs)
    return p.parse_string(string)
