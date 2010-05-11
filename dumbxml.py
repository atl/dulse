from xml.dom import pulldom
from xml.sax.saxutils import unescape
from types import StringTypes
from xml.dom import Node

def addtodict(dictionary, key, value):
    if not isinstance(dictionary, dict):
        raise TypeError("having trouble with some mixed content at node %s" % key)
    if key not in dictionary:
        dictionary[key] = value
    else:
        if not isinstance(dictionary[key], list):
            dictionary[key] = [dictionary[key], value]
        else:
            dictionary[key].append(value)
            

def getmixed(nodelist):
    out = ""
    if nodelist[0].nodeType == Node.TEXT_NODE:
        nodelist[0].data = nodelist[0].data.lstrip()
    if nodelist[-1].nodeType == Node.TEXT_NODE:
        nodelist[-1].data = nodelist[-1].data.lstrip()
    for node in nodelist:
        out += unescape(node.toxml())
    return out
    
def tonum(string):
    try:
        out = int(string)
    except ValueError:
        try:
            out = float(string)
        except ValueError:
            out = string
    return out

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
    def __init__(self, mixed=set(['body', 'content']), skip=set()):
        if isinstance(mixed, set):
            self.mixed = mixed
        else:
            self.mixed = set(mixed)
        self.skip = skip
        self.events = None
    
    def add_mixed(self, *args):
        for item in args:
            self.mixed.add(item)
        
    def add_skip(self, *args):
        for item in args:
            self.skip.add(item)
    
    def delete_mixed(self, *args):
        for item in args:
            self.mixed.discard(item)

    def delete_skip(self, *args):
        for item in args:
            self.skip.discard(item)
    
    def get_simple_xml_content(self, nodename):
        d = {}
        (event, currnode) = self.events.next()
        while currnode:
            if event == 'START_ELEMENT' and currnode.nodeName in self.mixed:
                self.events.expandNode(currnode)
                addtodict(d, currnode.nodeName, getmixed(currnode.childNodes))
            elif event == 'START_ELEMENT' and currnode.nodeName not in self.skip:
                addtodict(d, currnode.nodeName, self.get_simple_xml_content(currnode.nodeName))
            elif event == 'CHARACTERS' and currnode.data.strip():
                if isinstance(d, StringTypes):
                    d += unescape(currnode.data.lstrip())
                elif not d.keys():
                    d = unescape(currnode.data.lstrip())
                else:
                    raise TypeError("having trouble with some mixed content at node %s:\n%s\n\ntry SimpleXML.add_mixed('%s')" 
                                    % (nodename, currnode.data.strip(), nodename))
            elif event == 'END_ELEMENT' and currnode.nodeName == nodename:
                if isinstance(d, dict):
                    return d
                else:
                    return tonum(d)
            (event, currnode) = self.events.next()
    
    def parse(self, stream):
        self.events = pulldom.parse(stream)
        depth = 0
        d = {}
        for event, node in self.events:
            if event == 'START_ELEMENT' and depth == 0:
                depth += 1
            elif event == 'START_ELEMENT' and node.nodeName in self.mixed:
                self.events.expandNode(node)
                addtodict(d, node.nodeName, getmixed(node.childNodes))
            elif event == 'START_ELEMENT' and node.nodeName not in self.skip:
                addtodict(d, node.nodeName, self.get_simple_xml_content(node.nodeName))
        return d
    

