# excel-storage
Excel Storage

## Installation

    pip install excel-storage


## Usage

    from excel_storage import ExcelStorage

    def excelfunc():
        data = [
            {
                'Column 1': 1,
                'Column 2': 2,
            },
            {
                'Column 1': 3,
                'Column 2': 4,
            }
        ]
        fpath = ExcelStorage(data, 'my_data', font='name SimSum').save()


or

    from excel_storage import ExcelStorage

    def excelfunc():
        data = [
            ['Column 1', 'Column 2'],
            [1, 2],
            [3, 4]
        ]
        fpath = ExcelStorage(data, 'my_data', font='name SimSum').save()


or

    from excel_storage import ExcelStorage

    def excelfunc():
        data = [
            ['Column 1', 'Column 2'],
            [1, [2, 3]],
            [3, 4]
        ]
        fpath = ExcelStorage(data, 'my_data', font='name SimSum', merge_type='row_merge').save()


or

    from excel_storage import ExcelStorage

    def excelfunc():
        headers = ['Column 1', 'Column 2', 'Column 3', 'Column 4', 'Column 5']
        data = [['Value 1', [['Value 2 Row 1', [['Value 3', 'Value 4', [['Value 5']]]]], ['Value 2 Row 2', [['Value 3 Row 1', 'Value 4 Row 1', [['Value 5 Row 1']]], ['Value 3 Row 2', 'Value 4 Row 2', [['Value 5 Row 2']]]]]]]]
        fpath = ExcelStorage(data, 'my_data', font='name SimSum', merge_type='list_row_merge', headers=headers).save()


or

    from excel_storage import ExcelStorage

    def excelfunc():
        headers = ['Column 1', 'Column 2', 'Column 3', 'Column 4', 'Column 5']
        mapping = {
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
        data = [{
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
        fpath = ExcelStorage(data, 'my_data', font='name SimSum', merge_type='dict_row_merge', mapping=mapping, headers=headers).save()


## Params

  * font='name SimSum'
    * Set Font as SimSum(宋体)
  * force_csv=True
    * CSV Format? True for Yes, False for No, Default is False


## CSV

  ```python
  datas = [
      [u'中文', ]
  ]
  ```

|                 | Win Excel 2013 | Mac Excel 2011 | Mac Excel 2016 | Mac Numbers |
| --------------- | :------------: | :------------: | :------------: | :---------: |
| UTF8            | Messy          | Messy          | Messy          | Normal      |
| GB18030         | Normal         | Normal         | Normal         | Messy       |
| UTF8 + BOM_UTF8 | Normal         | Messy          | Normal         | Normal      |
| UTF16LE + BOM   |                |                |                |             |
