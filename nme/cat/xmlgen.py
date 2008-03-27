# A simple XML-generator# Originally Lars Marius Garshol, September 1998
# http://mail.python.org/pipermail/xml-sig/1998-September/000347.html
# Changes by Uche Ogbuji April 2003
# *  unicode support: accept encoding argument and use Python codecs
#    for correct character output
# *  switch from deprecated string module to string methods
# *  use PEP 8 style

import sys
import codecs

class XMLWriter:

    def __init__(self, out=sys.stdout, encoding="utf-8", indent=u"  "):
        """
        out      - a stream for the output
        encoding - an encoding used to wrap the output for unicode
        indent   - white space used for indentation
        """
        wrapper = codecs.lookup(encoding)[3]
        self.out = wrapper(out)
        self.stack = []
        self.indent = indent
        self.out.write(u'<?xml version="1.0" encoding="%s"?>\n' \
                       % encoding)

    def doctype(self, root, pubid, sysid):
        """
        Create a document type declaration (no internal subset)
        """
        if pubid == None:
            self.out.write(
                u"<!DOCTYPE %s SYSTEM '%s'>\n" % (root, sysid))
        else:
            self.out.write(
                u"<!DOCTYPE %s PUBLIC '%s' '%s'>\n" \
                % (root, pubid, sysid))
        
    def push(self, elem, attrs={}):
        """
        Create an element which will have child elements
        """
        self.__indent()
        self.out.write("<" + elem)
        for (a, v) in attrs.items():
            self.out.write(u" %s='%s'" % (a, self.__escape_attr(v)))
        self.out.write(u">\n")
        self.stack.append(elem)

    def elem(self, elem, content, attrs={}):
        """
        Create an element with text content only
        """
        self.__indent()
        self.out.write(u"<" + elem)
        for (a, v) in attrs.items():
            self.out.write(u" %s='%s'" % (a, self.__escape_attr(v)))
        self.out.write(u">%s</%s>\n" \
                       % (self.__escape_cont(content), elem))

    def empty(self, elem, attrs={}):
        """
        Create an empty element
        """
        self.__indent()
        self.out.write(u"<"+elem)
        for a in attrs.items():
            self.out.write(u" %s='%s'" % a)
        self.out.write(u"/>\n")
        
    def pop(self):
        """
        Close an element started with the push() method
        """
        elem=self.stack[-1]
        del self.stack[-1]
        self.__indent()
        self.out.write(u"</%s>\n" % elem)
    
    def __indent(self):
        self.out.write(self.indent * (len(self.stack) * 2))
    
    def __escape_cont(self, text):
        return text.replace(u"&", u"&amp;")\
               .replace(u"<", u"&lt;")

    def __escape_attr(self, text):
        return text.replace(u"&", u"&amp;") \
               .replace(u"'", u"&apos;").replace(u"<", u"&lt;")
