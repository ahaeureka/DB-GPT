#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   cleaner.py
@Time    :   2025/03/02 14:04:25
@Desc    :
'''

import pandas as pd
import numpy as np


class ExcelDataCleaner:
    def __init__(self, df: pd.DataFrame, col_type_mapping={}):
        """
        初始化数据清洗器
        :param file_path: Excel文件路径
        :param col_type_mapping: 列类型映射字典（可选），如 {'age': 'int', 'price': 'float'}
        """
        self.df = df
        self.clean_df = self.df.copy()
        self.type_mapping = col_type_mapping

    def _detect_actual_type(self, series):
        """自动检测列的实际数据类型（基于非空值）"""
        non_null = series.dropna()
        if non_null.empty:
            return 'object'

        # 类型优先级：数值型 > 时间型 > 字符型
        try:
            pd.to_numeric(non_null, errors='raise')
            return 'float' if any(non_null.astype('str').str.contains('\\.')) else 'int'
        except BaseException:
            try:
                pd.to_datetime(non_null, errors='raise')
                return 'datetime'
            except BaseException:
                return 'object'

    def _convert_type(self, series, target_type):
        """安全类型转换（处理混合类型）"""
        # 先转换为统一类型
        try:
            # 预处理：去除前后空格，并将空字符串替换为NaN（便于后续统一填充）
            if target_type == 'int':
                return pd.to_numeric(series, errors='coerce').fillna(0).astype(np.int64)
            elif target_type == 'float':
                # series = series.str.strip().replace(r'^\s*$', np.nan, regex=True)
                return pd.to_numeric(series, errors='coerce').fillna(0.0).astype(float)
            elif target_type == 'datetime':
                return pd.to_datetime(series, errors='coerce', format="%Y-%m-%d")
            else:
                return series.astype('str')
        except Exception as e:
            print(f"类型转换错误: {e}")
            return series.astype('object')

    def _clean_column(self, col_series, col_type):
        """单个列清洗流程"""
        # 空值处理
        if col_type in ['int', 'float']:
            cleaned = col_series.fillna(0 if col_type == 'int' else 0.0)
        elif col_type == 'datetime':
            cleaned = col_series.fillna(pd.NaT)
        else:
            cleaned = col_series.fillna('')

        # 类型强制转换
        return self._convert_type(cleaned, col_type)

    def clean_data(self):

        self.clean_df = self.df.copy()

        # 确定各列目标类型
        type_mapping = {
            col: self.type_mapping.get(col, self._detect_actual_type(self.clean_df[col]))
            for col in self.clean_df.columns
        }
        # 按列清洗
        for col in self.clean_df.columns:
            target_type = type_mapping[col]
            # print(f"clean col:{col}:{target_type}")
            self.clean_df[col] = self._clean_column(self.clean_df[col], target_type)

        # 最终类型校验
        for col in self.clean_df.columns:
            target_type = type_mapping[col]
            if target_type == 'int':
                self.clean_df[col] = self.clean_df[col].astype(np.int64)
            elif target_type == 'float':
                self.clean_df[col] = self.clean_df[col].astype(float)
        # 重命名execl 格式的列
        for col in self.clean_df.columns:
            new_col = self.excel_colunm_format(col)
            self.clean_df.rename(columns={col:new_col})

        return self

    def save_clean_data(self, output_path):
        """保存清洗后的数据"""
        if self.clean_df is not None:
            self.clean_df.to_excel(output_path, index=False)
            print(f"清洗后的数据已保存至: {output_path}")
        return self

    def get_clean_data(self):
        """获取清洗后的DataFrame"""
        return self.clean_df

    def __call__(self):
        return self.clean_data().get_clean_data()

    def excel_colunm_format(self, old_name: str) -> str:
        new_column = old_name.strip()
        new_column = new_column.replace(" ", "_")
        return new_column


if __name__ == "__main__":
    pass
