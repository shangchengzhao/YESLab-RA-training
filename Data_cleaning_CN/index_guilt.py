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
    def raw2long(df, 
              keep_columns = [], 
              DVname = []):
        ''' raw data to long format '''
        # if a column is missing according to keep_columns, add it
        for col in keep_columns:
            if col not in df.columns:
                df[col] = np.nan
        # return df
        
        selectrow = df[keep_columns + [col + '.response' for col in DVname] + [col + '.rt' for col in DVname]]
        # print(selectrow.columns)
        return selectrow
    
    # Define the patterns to search for
    DVname = ['slider_guilt', 'share_slider', 'slider_apology', \
            'slider_hide', 'slider_forgiveness', 'slider_mad']

    # Filter columns based on the specified patterns
    subject_info = ['participant', 'date', 'chooserow', \
                        'stipic', 'type_trial', 'DV', \
                        'judge.clicked_name','answer', 'incompleteTrials']
    
    # call the function
    selectrow = raw2long(df, 
                        keep_columns=subject_info,
                        DVname=DVname)
    
    attention_check = df.dropna(subset=['answer']).query("answer == 'RightButton' or answer == 'LeftButton'")
    acc = np.mean(attention_check['judge.clicked_name'] == attention_check['answer'])
    if acc > 0.8:
        print(f"Participant {selectrow['participant'][0]} acc = {acc}")
    else:
        print(f"Participant {selectrow['participant'][0]} acc = {acc} < 0.8 *****")

    result = None
    result = int(acc * 100)

    #返回结果（int / float 类型）
    return result