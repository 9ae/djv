"""Defining the Page component"""

from __future__ import unicode_literals

import brain.webnode as webnode
import brain.webnode.html as h
import time

class Page(webnode.Component):
    def get_title(self):
        return 'Deja Vu'

    def header(self):
        z = []
        with h.div(class_='navbar navbar-inverse navbar-fixed-top',
                role='navigation').into(z):
            with h.div(class_='container').into(z):
                with h.div(class_='collapse navbar-collapse').into(z):
                    with h.ul(class_='nav navbar-nav').into(z):
                        with h.li().into(z):
                            z += h.a('Home', href='/webnode/media')
        return z

    def content(self):
        return []

    def footer(self):
        z = []
        z += h.p('This page is generated on %s' % time.asctime())
        return z

    def tree(self):
        z = []
        z += h.Raw('<!DOCTYPE html>')
        with h.head().into(z):
            z += h.title(self.get_title())
            z += webnode.external.BootstrapCSS()
            z += webnode.external.BootstrapJS()
            z += h.script(src='http://player.kaltura.com/mwEmbedLoader.php', charset='utf-8')
            #z += webnode.external.DataTablesCSS()
            #z += webnode.external.DataTablesJS()
            #z += h.link(rel='stylesheet', href='static/foodie.css')
        with h.body(style='padding-top: 70px;').into(z):
            with h.div(id='header', class_='container').into(z):
                z += self.header()
            with h.div(id='content', class_='container theme-showcase',
                        role='main').into(z):
                    z += self.content()
            with h.div(id='footer', class_='container').into(z):
                z += self.footer()

        return z
