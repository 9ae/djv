"""Defining the base Component class."""

class Component:
    """A representation of an element on a webpage.

    A subclass of Component should either define the render() method and the
    render_plaintext() method, or the tree() method, but not both.
    """
    def render(self):
        """Return the HTML representation"""
        ret = ''.join(c.render() for c in self.tree())
        return ret

    def render_plaintext(self):
        """Return the plain text representation"""
        ret = ''.join(c.render_plaintext() for c in self.tree())
        return ret

    def tree(self):
        """Return the list of sub-components"""
        return [self]

    def __iter__(self):
        """Return an iterator for the component's sub-components

        This allows us to write, for example,
        z += some_component
        """
        return iter(self.tree())
