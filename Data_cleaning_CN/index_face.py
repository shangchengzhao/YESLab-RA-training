# -*- coding: utf-8 -*-

from io import BytesIO
import pandas as pd
import numpy as np

def handler(event, context):
    '''
    分析数据的入口函数，函数名必须为`handler`不能更改。
    以实验产生的CSV作为数据，计算出**一个数值**并返回，
    脑岛项目会将该数值作为对应实验节点的分数

    Parameters:
        event - 以二进制传输的CSV字符，可通过`BytesIO`读取为CSV文件
        context - 上下文，无需对此参数进行操作

    Returns:
        返回一个int或float类型的数值，类型不对会导致返回错误。
        如果不确定数值类型可以对返回值进行显式类型转换，例如
        return int(result)
    '''
    
    # 读取数据文件到DataFrame
    data_file = BytesIO(event)
    df = pd.read_csv(data_file, encoding='utf-8')

    # 分析数据
    # step1: long format
    def raw2long_trait(df, 
                   keep_columns=[],
                   DVname=[]):
        """
        Convert the DataFrame from wide to long format
        """
        # select columns
        colinterest = keep_columns + [col + '.response' for col in DVname] + [col + '.rt' for col in DVname]
        for col in colinterest:
            if col not in df.columns:
                df[col] = np.nan
        selectrow = df[colinterest]

        acc = 0
        attention_check = selectrow.dropna(subset=['isCheck']).query("isCheck == 1")
        acc = np.mean(np.logical_and(attention_check['slider_face_judge.response'] > attention_check['answer']-0.5,
                                        attention_check['slider_face_judge.response'] < attention_check['answer']+0.5))

        return acc
    
    # call the function
    sub_info = ['isCheck', 'answer']
    exp_info = ['slider_face_judge']
    acc = raw2long_trait(df, 
                        keep_columns=sub_info,
                        DVname = exp_info)
    print(acc)

    result = None
    result = int(acc * 100)

    #返回结果（int / float 类型）
    return result