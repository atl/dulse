try:
    from xml.etree import cElementTree as etree
except ImportError:
    from xml.etree import ElementTree as etree

def to_xml(obj, root="data", encoding=None):
    return etree.tostring(to_etree_element(obj, root=root), encoding=encoding)

def write(obj, filename, root="data", encoding="UTF-8"):
    to_etree(obj, root=root).write(filename, encoding=encoding)

def to_etree(obj, root="data"):
    return etree.ElementTree(to_etree_element(obj, root=root))

def to_etree_element(obj, root="data"):
    root_element = etree.Element(root)
    if isinstance(obj, (basestring, float, int)):
        root_element.text = unicode(obj)
    else:
        for key, value in obj.iteritems():
            if isinstance(value, list):
                for a in value:
                    root_element.append(_to_element(key, a))
            else:
                root_element.append(_to_element(key, value))
    return root_element

def _to_element(tag, content):
    e = etree.Element(tag)
    if content is None:
        return e
    if isinstance(content, (basestring, float, int)):
        e.text = unicode(content)
        return e
    if isinstance(content, dict):
        for key, value in content.iteritems():
            if isinstance(value, list):
                for a in value:
                    e.append(_to_element(key, a))
            else:
                e.append(_to_element(key, value))
        return e


