"""Define the DataTables Component"""

from __future__ import unicode_literals

from component import Component
import html as h
import json

class DTable(Component):
    """A table component using DataTables"""
    def __init__(self, headers, data, use_index_column=True):
        # a unique ID for the table
        self.id = 'dtable%d' % id(self)
        self.use_index_column = use_index_column
        self.headers = headers
        self.data = data

    def tree(self):
        z = []
        z += h.table(id=self.id, class_='display', cellspacing='0', width='100%')
        if self.use_index_column:
            js_headers = json.dumps([{'title': item} for item in ([''] + self.headers)],
                    ensure_ascii=False, encoding='utf8')
            js_data = json.dumps([([''] + row) for row in self.data], ensure_ascii=False, encoding='utf8')
        else:
            js_headers = json.dumps([{'title': item} for item in self.headers],
                    ensure_ascii=False, encoding='utf8')
            js_data = json.dumps(self.data, ensure_ascii=False, encoding='utf8')
        js = '''\
$(document).ready(function() {
    var data = %(js_data)s;
    var headers = %(js_headers)s;
    var t = $('#%(id)s').DataTable({
        "data": data,
        "columns": headers,
        "columnDefs": [ {
            "searchable": false,
            "orderable": false,
            "targets": 0,
        } ],
        "order": [[ 1, 'asc' ]],
        "dom": 'lfTC<"clear">rtip',
        "tableTools": {
            "sSwfPath": "/static/datatables/extensions/TableTools/swf/copy_csv_xls_pdf.swf"
        },
        "lengthMenu": [[-1, 25], ["All", 25]],
        "autoWidth": false,
    });
    //new $.fn.dataTable.FixedHeader( t , {
    //    "offsetTop": 50
    //    });
    t.on( 'order.dt search.dt', function () {
        t.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
            cell.innerHTML = i+1;
        } );
    } ).draw();
} );
''' % {
    'js_data': js_data,
    'js_headers': js_headers,
    'id': self.id,
}
        z += h.script(js, type='text/javascript')
        return z