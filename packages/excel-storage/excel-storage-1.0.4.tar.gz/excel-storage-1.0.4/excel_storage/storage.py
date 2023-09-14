# -*- coding:utf-8 -*-

import datetime

from excel_base import (BytesIO, StringIO, as_csv, as_dict_row_merge_xls, as_list_row_merge_xls, as_row_merge_xls,
                        as_xls, is_py2, use_xls_or_not)


# Min (Max. Rows) for Widely Used Excel
# http://superuser.com/questions/366468/what-is-the-maximum-allowed-rows-in-a-microsoft-excel-xls-or-xlsx
EXCEL_MAXIMUM_ALLOWED_ROWS = 65536
# Column Width Limit For ``xlwt``
# https://github.com/python-excel/xlwt/blob/master/xlwt/Column.py#L22
EXCEL_MAXIMUM_ALLOWED_COLUMN_WIDTH = 65535


def __init__(self, data, output_name='excel_data', format='%Y%m%d%H%M%S', headers=None, force_csv=False, encoding='utf-8-sig', font=None, sheet_name='Sheet 1', blanks_for_none=True, auto_adjust_width=True, min_cell_width=1000, vert=0x01, horz=0x01, hvert=0x01, hhorz=0x02, merge_type=None, mapping=None, timezone=None):
    self.data = data
    self.output_name = output_name
    self.format = format
    self.headers = headers
    self.force_csv = force_csv
    self.encoding = encoding
    self.font = font
    self.sheet_name = sheet_name
    self.blanks_for_none = blanks_for_none
    self.auto_adjust_width = auto_adjust_width
    self.min_cell_width = min_cell_width
    self.file_ext = None
    # VERT_TOP     = 0x00    顶端对齐
    # VERT_CENTER  = 0x01    居中对齐（垂直方向上）
    # VERT_BOTTOM  = 0x02    底端对齐
    # HORZ_LEFT    = 0x01    左端对齐
    # HORZ_CENTER  = 0x02    居中对齐（水平方向上）
    # HORZ_RIGHT   = 0x03    右端对齐
    self.vert = vert
    self.horz = horz
    self.hvert = hvert
    self.hhorz = hhorz
    self.mapping = mapping
    self.timezone = timezone

    if merge_type != 'dict_row_merge':
        if not isinstance(self.data, dict):
            self.data = {self.sheet_name: {'data': self.data, 'headers': self.headers}}

        # Make sure we've got the right type of data to work with
        # ``list index out of range`` if data is ``[]``
        valid_data = True
        for sheet_name, sheet_info in self.data.items():
            sheet_data = sheet_info.get('data') or []
            sheet_headers = sheet_info.get('headers')
            if not hasattr(sheet_data, '__getitem__'):
                valid_data = False
                break
            if isinstance(sheet_data[0], dict):
                if sheet_headers is None:
                    sheet_headers = list(sheet_data[0].keys())
                sheet_data = [[row[col] for col in sheet_headers] for row in sheet_data]
            if not hasattr(sheet_data[0], '__getitem__'):
                valid_data = False
                break
            if sheet_headers and not hasattr(sheet_headers[0], '__getitem__'):
                valid_data = False
                break
            sheet_info['data'] = sheet_data
            sheet_info['headers'] = sheet_headers
            self.data[sheet_name] = sheet_info
        assert valid_data is True, 'ExcelStorage requires a sequence of sequences'

    self.output = StringIO() if is_py2 else BytesIO()
    if merge_type == 'row_merge':
        _, file_ext = (self.as_row_merge_xls, 'xls')
    elif merge_type == 'list_row_merge':
        _, file_ext = (self.as_list_row_merge_xls, 'xls')
    elif merge_type == 'dict_row_merge':
        _, file_ext = (self.as_dict_row_merge_xls, 'xls')
    else:
        # Excel has a limit on number of rows; if we have more than that, make a csv
        _, file_ext = (self.as_xls, 'xls') if self.use_xls_or_not else (self.as_csv, 'csv')
    self.output.seek(0)

    self.file_ext = file_ext


def save(self):
    file_name_ext = '_{0}'.format(datetime.datetime.now().strftime(self.format)) if self.format else ''
    final_file_name = ('%s%s.%s' % (self.output_name, file_name_ext, self.file_ext)).replace('"', '\"')

    with open(final_file_name, 'wb') as writer:
        writer.write(self.output.getvalue())

    return final_file_name


clsdict = {
    'EXCEL_MAXIMUM_ALLOWED_ROWS': EXCEL_MAXIMUM_ALLOWED_ROWS,
    'EXCEL_MAXIMUM_ALLOWED_COLUMN_WIDTH': EXCEL_MAXIMUM_ALLOWED_COLUMN_WIDTH,
    '__init__': __init__,
    'use_xls_or_not': use_xls_or_not,
    'as_xls': as_xls,
    'as_row_merge_xls': as_row_merge_xls,
    'as_list_row_merge_xls': as_list_row_merge_xls,
    'as_dict_row_merge_xls': as_dict_row_merge_xls,
    'as_csv': as_csv,
    'save': save,
}


ExcelStorage = type('ExcelStorage', (object, ), clsdict)
