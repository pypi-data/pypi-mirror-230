import re
import os
import time

def extract_year_month_from_filename(file_name):
    # 定义日期匹配的正则表达式
    date_pattern = r"\d{4}\d{2}"  # 匹配8位数字，前4位表示年份，后2位表示月份

    # 在文件名中搜索日期信息
    match = re.search(date_pattern, file_name)
    if match:
        date_str = match.group()
        year = int(date_str[:4])
        month = int(date_str[4:6])
        return year, month
    else:
        return None, None
    


def get_year_and_month_from_timestamp(timestamp):
    # 将时间戳转换为本地时间的元组
    time_tuple = time.localtime(timestamp)

    # 从时间元组中提取出年份和月份
    year = time_tuple.tm_year
    month = time_tuple.tm_mon

    return year, month

def get_last_modified_time(file_path):
    try:
        # 获取文件的最后修改时间的时间戳
        timestamp = os.path.getmtime(file_path)

        # 提取出年份和月份
        year, month = get_year_and_month_from_timestamp(timestamp)

        return year, month
    except Exception as e:
        print(f"获取文件最后修改时间失败：{e}")
        return None, None