"""External CSS and Javascript resources"""

from __future__ import unicode_literals

import html as h
from component import Component

def make_CSS_component(stylesheets):
    class CSSComponent(Component):
        def tree(self):
            z = []
            for stylesheet in stylesheets:
                z += h.link(rel='stylesheet', href=stylesheet)
            return z
    return CSSComponent

def make_JS_component(scripts):
    class JSComponent(Component):
        def tree(self):
            z = []
            for script in scripts:
                z += h.script(src=script)
            return z
    return JSComponent

BootstrapCSS = make_CSS_component([
    '//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css',
    '//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap-theme.min.css',
])

BootstrapJS = make_JS_component([
    'https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js',
    '//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js',
])

DataTablesCSS = make_CSS_component([
    '/static/datatables/media/css/jquery.dataTables.min.css',
    '/static/datatables/extensions/TableTools/css/dataTables.tableTools.min.css',
    '/static/datatables/extensions/ColVis/css/dataTables.colVis.min.css',
    '/static/datatables/extensions/FixedHeader/css/dataTables.fixedHeader.min.css',
])

DataTablesJS = make_JS_component([
    '/static/datatables/media/js/jquery.dataTables.min.js',
    '/static/datatables/extensions/TableTools/js/dataTables.tableTools.min.js',
    '/static/datatables/extensions/ColVis/js/dataTables.colVis.min.js',
    '/static/datatables/extensions/FixedHeader/js/dataTables.fixedHeader.min.js',
])

#    z += h.Link(rel = 'stylesheet', type = 'text/css', href = '/static/960_12_col.css')
#    z += h.Link(rel = 'stylesheet', type = 'text/css', href = '/static/nv.d3.css')
#    z += h.Link(rel = 'stylesheet', type = 'text/css', href = '/static/d.css')
#    z += h.Link(rel = 'shortcut icon', href = '/static/favicon.ico')
#    z += h.Script(src = 'https://www.google.com/jsapi', type = 'text/javascript')
#    z += h.Script(src = '/static/d3.v3.min.js', charset='utf-8')
#    z += h.Script(src = '/static/nv.d3.min.js', charset='utf-8')