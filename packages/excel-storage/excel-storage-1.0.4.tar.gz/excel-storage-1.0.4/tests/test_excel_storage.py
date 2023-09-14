# -*- coding: utf-8 -*-

from excel_storage import ExcelStorage


class TestDjangoExcelStorageCommands(object):

    def setup_class(self):
        self.data1 = [{
            'Column 1': 1,
            'Column 2': 2,
        }, {
            'Column 1': 3,
            'Column 2': 4,
        }]
        self.data2 = [
            ['Column 1', 'Column 2'],
            [1, 2],
            [3, 4]
        ]
        self.data3 = [
            ['Column 1', 'Column 2'],
            [1, [2, 3]],
            [3, 4]
        ]

        self.sheet_name1 = 'Sheet 1'
        self.sheet_name2 = 'Sheet 2'
        self.sheet_name3 = 'Sheet 3'

        self.sheet_data1 = {'Sheet 1': {'data': [[1, 2], [3, 4]], 'headers': ['Column 1', 'Column 2']}}
        self.sheet_data11 = self.sheet_data1
        self.sheet_data2 = {'Sheet 1': {'data': [['Column 1', 'Column 2'], [1, 2], [3, 4]], 'headers': None}}
        self.sheet_data22 = {'Sheet 2': {'data': [['Column 1', 'Column 2'], [1, 2], [3, 4]], 'headers': None}}
        self.sheet_data3 = {'Sheet 1': {'data': [['Column 1', 'Column 2'], [1, [2, 3]], [3, 4]], 'headers': None}}
        self.sheet_data33 = {'Sheet 3': {'data': [['Column 1', 'Column 2'], [1, [2, 3]], [3, 4]], 'headers': None}}

        self.headers = ['Column 1', 'Column 2', 'Column 3', 'Column 4', 'Column 5']
        self.mapping = {
            'field_key': 'Column 1',
            'data_key': 'Children 1',
            'next': {
                'field_key': 'Column 2',
                'data_key': 'Children 2',
                'next': {
                    'field_key': ['Column 3', 'Column 4'],
                    'data_key': 'Children 3',
                    'next': {
                        'field_key': 'Column 5',
                    }
                }
            }
        }
        self.rawdata = [{
            'Column 1': 'Value 1',
            'Column 11': 'Value 11',
            'Children 1': [{
                'Column 2': 'Value 2 Row 1',
                'Column 22': 'Value 22 Row 1',
                'Children 2': [{
                    'Column 3': 'Value 3',
                    'Column 4': 'Value 4',
                    'Children 3': {
                        'Column 5': 'Value 5',
                    }
                }]
            }, {
                'Column 2': 'Value 2 Row 2',
                'Column 22': 'Value 22 Row 2',
                'Children 2': [{
                    'Column 3': 'Value 3 Row 1',
                    'Column 4': 'Value 4 Row 1',
                    'Children 3': {
                        'Column 5': 'Value 5 Row 1',
                    }
                }, {
                    'Column 3': 'Value 3 Row 2',
                    'Column 4': 'Value 4 Row 2',
                    'Children 3': {
                        'Column 5': 'Value 5 Row 2',
                    }
                }]
            }]
        }]
        self.preprocesseddata = [['Value 1', [['Value 2 Row 1', [['Value 3', 'Value 4', [['Value 5']]]]], ['Value 2 Row 2', [['Value 3 Row 1', 'Value 4 Row 1', [['Value 5 Row 1']]], ['Value 3 Row 2', 'Value 4 Row 2', [['Value 5 Row 2']]]]]]]]

    def test_as_csv(self):
        csv1 = ExcelStorage(self.data1, 'my_data', force_csv=True, font='name SimSum')
        assert isinstance(csv1, ExcelStorage)
        assert csv1.data == self.sheet_data1

        csv2 = ExcelStorage(self.data2, 'my_data', force_csv=True, font='name SimSum')
        assert isinstance(csv2, ExcelStorage)
        assert csv2.data == self.sheet_data2

        csv3 = ExcelStorage(self.data3, 'my_data', force_csv=True, font='name SimSum')
        assert isinstance(csv3, ExcelStorage)
        assert csv3.data == self.sheet_data3

    def test_as_xls(self):
        xls1 = ExcelStorage(self.data1, 'my_data', font='name SimSum')
        assert isinstance(xls1, ExcelStorage)
        assert xls1.data == self.sheet_data1

        xls2 = ExcelStorage(self.data2, 'my_data', font='name SimSum')
        assert isinstance(xls2, ExcelStorage)
        assert xls2.data == self.sheet_data2

        # xls3 = ExcelResponse(self.data3, 'my_data', font='name SimSum')
        # assert isinstance(xls3, ExcelStorage)

        xls11 = ExcelStorage({
            self.sheet_name1: {'data': self.data1},
        }, 'my_data', font='name SimSum')
        assert isinstance(xls11, ExcelStorage)
        assert xls11.data == self.sheet_data11

        xls22 = ExcelStorage({
            self.sheet_name2: {'data': self.data2},
        }, 'my_data', font='name SimSum')
        assert isinstance(xls22, ExcelStorage)
        assert xls22.data == self.sheet_data22

    def test_as_row_merge_xls(self):
        xls1 = ExcelStorage(self.data1, 'my_data', font='name SimSum', merge_type='row_merge')
        assert isinstance(xls1, ExcelStorage)
        assert xls1.data == self.sheet_data1

        xls2 = ExcelStorage(self.data2, 'my_data', font='name SimSum', merge_type='row_merge')
        assert isinstance(xls2, ExcelStorage)
        assert xls2.data == self.sheet_data2

        xls3 = ExcelStorage(self.data3, 'my_data', font='name SimSum', merge_type='row_merge')
        assert isinstance(xls3, ExcelStorage)
        assert xls3.data == self.sheet_data3

        xls11 = ExcelStorage({
            self.sheet_name1: {'data': self.data1},
        }, 'my_data', font='name SimSum', merge_type='row_merge')
        assert isinstance(xls11, ExcelStorage)
        assert xls11.data == self.sheet_data11

        xls22 = ExcelStorage({
            self.sheet_name2: {'data': self.data2},
        }, 'my_data', font='name SimSum', merge_type='row_merge')
        assert isinstance(xls22, ExcelStorage)
        assert xls22.data == self.sheet_data22

        xls33 = ExcelStorage({
            self.sheet_name3: {'data': self.data3},
        }, 'my_data', font='name SimSum', merge_type='row_merge')
        assert isinstance(xls33, ExcelStorage)
        assert xls33.data == self.sheet_data33

    def test_as_list_row_merge_xls(self):
        xls1 = ExcelStorage(self.preprocesseddata, 'my_data', font='name SimSum', merge_type='list_row_merge')
        assert isinstance(xls1, ExcelStorage)

        xls2 = ExcelStorage(self.preprocesseddata, 'my_data', font='name SimSum', merge_type='list_row_merge', headers=self.headers)
        assert isinstance(xls2, ExcelStorage)

        xls11 = ExcelStorage({
            self.sheet_name1: {'data': self.preprocesseddata},
        }, 'my_data', font='name SimSum', merge_type='list_row_merge')
        assert isinstance(xls11, ExcelStorage)

        xls22 = ExcelStorage({
            self.sheet_name2: {'data': self.preprocesseddata},
        }, 'my_data', font='name SimSum', merge_type='list_row_merge', headers=self.headers)
        assert isinstance(xls22, ExcelStorage)

    def test_as_dict_row_merge_xls(self):
        xls1 = ExcelStorage(self.rawdata, 'my_data', font='name SimSum', merge_type='dict_row_merge', mapping=self.mapping)
        assert isinstance(xls1, ExcelStorage)

        xls2 = ExcelStorage(self.rawdata, 'my_data', font='name SimSum', merge_type='dict_row_merge', mapping=self.mapping, headers=self.headers)
        assert isinstance(xls2, ExcelStorage)

        xls11 = ExcelStorage({
            self.sheet_name2: {
                'data': self.rawdata,
                'mapping': self.mapping,
                'headers': self.headers,
            },
        }, 'my_data', font='name SimSum', merge_type='dict_row_merge')
        assert isinstance(xls11, ExcelStorage)

        xls22 = ExcelStorage({
            self.sheet_name2: {
                'data': self.rawdata,
                'mapping': self.mapping,
                'headers': self.headers,
            },
        }, 'my_data', font='name SimSum', merge_type='dict_row_merge', headers=self.headers)
        assert isinstance(xls22, ExcelStorage)
