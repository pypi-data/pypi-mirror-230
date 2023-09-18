'''
Descripttion:
version:
Author: whs2233
Date: 2023-06-25 15:39:55
LastEditors: whs
LastEditTime: 2023-06-26 15:48:34
'''
import json
from decimal import Decimal
import os
import csv


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


def read_json(file):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data


def write_json(file, content):
    directory = os.path.dirname(file)
    os.makedirs(directory, exist_ok=True)
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, cls=DecimalEncoder)


def read_csv(file):
    # utf-8-sig 必须是这个编码格式 否则首个数据会出现 \ufeff 是一个特殊的字符，通常表示文件的开始
    with open(file, newline='', encoding='utf-8-sig') as csvfile:
        csv_reader = csv.reader(csvfile)
        data = []
        first = []
        for row in csv_reader:
            if len(first) == 0:
                first = row
            else:
                new_arr = {}
                for idx, val in enumerate(row):
                    key = first[idx]
                    new_arr[key] = val
                data.append(new_arr)
    return data


def write_file(file, content, mode='w'):
    directory = os.path.dirname(file)
    os.makedirs(directory, exist_ok=True)
    with open(file, mode, encoding='utf-8') as f:
        f.write(content)


def read_file(file):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
        return content


if __name__ == "__main__":
    csv = read_csv('../data/channel.csv')
    print(csv)
