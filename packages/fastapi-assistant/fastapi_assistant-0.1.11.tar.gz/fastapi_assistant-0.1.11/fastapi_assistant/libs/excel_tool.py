import os
import random
from io import BytesIO
from typing import List

import numpy as np
from fastapi.responses import StreamingResponse
import pandas as pd
from styleframe import StyleFrame


def export_exl(header: List[str], data, file_name='download.xlsx') -> StreamingResponse:
    output = BytesIO()
    df = pd.DataFrame(columns=header)
    for item in data:
        df.loc[len(df.index)] = item

    excel_writer = StyleFrame.ExcelWriter(output)

    sf = StyleFrame(df)
    sf.to_excel(
        excel_writer=excel_writer,
        best_fit=header,
        columns_and_rows_to_freeze='B2',
        row_to_add_filters=0,
    )
    excel_writer.close()
    output.seek(0)
    headers = {"content-type": "application/vnd.ms-excel",
               "content-disposition": 'attachment;filename={}'.format(file_name.encode("utf-8").decode("latin1"))}
    return StreamingResponse(output, media_type='xls/xlsx', headers=headers)


class ExcelTools:
    def __init__(self, columns_map=None, order=None):
        """
        :param columns_map: 列名映射 => {"name":"姓名"，"score":"成绩","sex":"性别"}
        :param columns_map: 列排序列表 => ["name","sex","score"]
        """
        self.columns_map = columns_map
        self.order = order

    def excel_to_df(self, excel, skip_rows=0) -> pd.DataFrame:
        fx = excel.read()
        file_name = ''.join(random.choice("0123456789abcdefgh") for i in range(16)) + '.xlsx'
        with open(file_name, 'wb') as f:
            f.write(fx)

        df = pd.read_excel(file_name, skiprows=skip_rows)
        os.remove(file_name)
        df = df.replace(np.nan, '', regex=True)

        # 去除所有列数据中的空格
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # 列名映射
        if self.columns_map:
            columns_map = dict(zip(self.columns_map.values(), self.columns_map.keys()))
            df = df.rename(columns=columns_map)

        return df

    def excel_to_dict(self, excel, skip_rows=0):
        """
        Excel转Python dict
        :param excel:
        :param skip_rows:
        :return:
        """
        if not excel:
            return []
        df = self.excel_to_df(excel, skip_rows=skip_rows)
        result = df.to_dict(orient='records')
        return result

    def dict_to_excel(self, datas):
        """
        :param datas: 数据集 => [{"name":"张三","score":90，"sex":"男"}]
        :return:
        """
        output = BytesIO()
        pf = pd.DataFrame(datas)
        if self.order:
            pf = pf[self.order]
        # 将列名替换为中文
        if self.columns_map:
            pf.rename(columns=self.columns_map, inplace=True)
        # 指定生成的Excel表格名称
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        pf.fillna(' ', inplace=True)
        pf.to_excel(writer, sheet_name='sheet1', index=False)
        workbook = writer.book
        worksheet = writer.sheets['sheet1']

        for i, col in enumerate(pf.columns):
            column_len = pf[col].astype(str).str.len().max()
            column_len = max(column_len, len(col)) + 2
            worksheet.set_column(i, i, column_len)
        writer.close()
        output.seek(0)
        return output
