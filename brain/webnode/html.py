"""Define common HTML elements"""

from component import Component

class Raw(Component):
    """Raw HTML code"""
    def __init__(self, raw):
        self.raw = raw

    def render(self):
        return self.raw

    def render_plaintext(self):
        return ''

class Text(Component):
    """Raw HTML text"""
    def __init__(self, text):
        self.text = text

    def render(self):
        return self.text

    def render_plaintext(self):
        return self.text

class StartTag(Raw):
    """Represent a start tag in HTML"""
    def __init__(self, tag, attrs=None):
        self.tag = tag
        if attrs:
            if 'class_' in attrs: attrs['class'] = attrs.pop('class_')
            attr = ' '.join('%s="%s"' % kv for kv in attrs.iteritems())
            self.raw = '<%s %s>' % (tag, attr)
        else:
            self.raw = '<%s>' % tag

    def __repr__(self):
        return '<StartTag %s>' % self.tag

class EndTag(Raw):
    """Represent an end tag in HTML"""
    def __init__(self, tag, attrs=None):
        self.tag = tag
        self.raw = '</%s>' % tag

    def __repr__(self):
        return '<EndTag %s>' % self.tag

class VoidHTMLElement(Raw):
    """Represent a void HTML element

    A void HTML element has a start tag but no end tag.
    """
    def __init__(self, **attrs):
        tag = self.__class__.__name__.lower()
        self.raw = StartTag(tag, attrs).render()

class NormalHTMLElement(Component):
    """Represent a normal HTML element

    A normal HTML element has a start tag and an end tag.
    """
    def __init__(self, text=None, **attrs):
        """Construct a normal element with given text content"""
        self.tag = self.__class__.__name__.lower()
        self.text = text
        self.attrs = attrs

    def __enter__(self):
        self.z += StartTag(self.tag, self.attrs)

    def __exit__(self, type, value, traceback):
        self.z += EndTag(self.tag)

    def into(self, z):
        self.z = z
        return self

    def render(self):
        return ''.join([
            StartTag(self.tag, self.attrs).render(),
            self.text or '',
            EndTag(self.tag).render(),
        ])

    def render_plaintext(self):
        return self.text or ''

# Define common HTML elements
# Note that their class names are in lower case following the HTML convention
class a(NormalHTMLElement): pass
class body(NormalHTMLElement): pass
class dd(NormalHTMLElement): pass
class div(NormalHTMLElement): pass
class dl(NormalHTMLElement): pass
class dt(NormalHTMLElement): pass
class form(NormalHTMLElement): pass
class h1(NormalHTMLElement): pass
class h2(NormalHTMLElement): pass
class h3(NormalHTMLElement): pass
class head(NormalHTMLElement): pass
class html(NormalHTMLElement): pass
class iframe(NormalHTMLElement): pass
class img(VoidHTMLElement): pass
class input(NormalHTMLElement): pass
class li(NormalHTMLElement): pass
class link(VoidHTMLElement): pass
class p(NormalHTMLElement): pass
class pre(NormalHTMLElement): pass
class script(NormalHTMLElement): pass
class span(NormalHTMLElement): pass
class svg(NormalHTMLElement): pass
class table(NormalHTMLElement): pass
class tbody(NormalHTMLElement): pass
class td(NormalHTMLElement): pass
class textarea(NormalHTMLElement): pass
class tfoot(NormalHTMLElement): pass
class th(NormalHTMLElement): pass
class thead(NormalHTMLElement): pass
class title(NormalHTMLElement): pass
class tr(NormalHTMLElement): pass
class ul(NormalHTMLElement): pass
