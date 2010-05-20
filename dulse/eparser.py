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

def STRING(string):
    try:
        return string.strip()
    except AttributeError:
        return None

def NO_CONVERSION(string):
    return string

class SimpleXMLParser(object):
    """
    Simple XML parser class that completely disregards attributes, and
    mostly disregards order. Text nodes are returned as strings, elements
    are returned as dict entries. Elements with mixed content must be identified
    with the `mixed` argument (or with add_mixed and delete_mixed methods), 
    and are returned as a string of their contents.
    
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
        {u'author': u'Me',
         u'content': u"<h1>Chapter 1</h1><p><em>These</em> are the times that\n    try mens' soles....</p>",
         u'date': u'23 April 2009',
         u'endnote': [u'This is the first.', u'This is the last.'],
         u'title': u'My Book'}
    
    """
    def __init__(self, conversion=None, mixed_content=True):
        self.events = None
        if conversion:
            self.conversion = conversion
        else:
            self.conversion = NUMBER
        if not mixed_content:
            self.is_mixed = lambda x: False
    
    @staticmethod
    def is_mixed(ele):
        return bool((none_strip(ele.text) and ele.getchildren()) or 
            any(map(lambda x: none_strip(x.tail), ele.getchildren())))

    @staticmethod
    def get_mixed(z):
        if z.text:
            y = z.text + ''.join(map(etree.tostring, z.getchildren()))
        else:
            y = ''.join(map(etree.tostring, z.getchildren()))
        return y.strip()
    
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
