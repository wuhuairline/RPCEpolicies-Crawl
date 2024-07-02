
import csv
import os
import requests
import time
import random
from bs4 import BeautifulSoup
import chardet

def random_sleep(min_seconds, max_seconds):
    """
    在给定的时间范围内随机暂停。
    :param min_seconds: 最小等待时间（秒）
    :param max_seconds: 最大等待时间（秒）
    """
    sleep_time = random.uniform(min_seconds, max_seconds)
    time.sleep(sleep_time)

# 创建一个目录来保存爬取的文本文件
output_dir = 'D:/桌面文件/BIT_管理科学与工程_博士/论文1/数据收集/文本'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 创建一个字典来跟踪每个日期的文件编号
date_counter = {}

# 初始化记录位置，默认从第一行开始
current_row = 0

record_file_path = 'D:/桌面文件/BIT_管理科学与工程_博士/论文1/数据收集/pre_record.txt'
csv_file_path = 'D:/桌面文件/BIT_管理科学与工程_博士/论文1/数据收集/列表/合并数据_列表.csv'

# 检查是否存在记录文件，如果存在，则读取记录
if os.path.exists(record_file_path):
    with open(record_file_path, 'r') as record_file:
        current_row = int(record_file.read())

# 检查已有文件，以确定新文件的起始编号
for file_name in os.listdir(output_dir):
    if file_name.endswith('.txt'):
        parts = file_name.split('_')
        if len(parts) >= 3:
            date = '_'.join(parts[:3])
            num = int(parts[3].split('.')[0])
            date_counter[date] = max(date_counter.get(date, 0), num)

# 打开CSV文件并读取数据
with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
    csvreader = csv.DictReader(csvfile)

    # 跳过已爬取的记录
    for _ in range(current_row):
        next(csvreader, None)

    for index, row in enumerate(csvreader, start=current_row + 1):
        title = row['标题']
        url = row['URL']
        publish_time = row['发布时间'].replace('/', '_')

        # 设置随机暂停以掩盖爬虫行为
        random_sleep(1, 5)  # 例如，随机等待1到5秒

        # 发送HTTP请求获取网页内容
        response = requests.get(url)
        if response.status_code == 200:
            encoding = chardet.detect(response.content)['encoding']
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding=encoding)
            text_elements = soup.find_all('p')
            text_content = '\n'.join([element.text.strip() for element in text_elements])

            # 获取日期对应的编号，如果日期没有出现过，则编号从上一个最高编号+1开始
            date_counter.setdefault(publish_time, 0)
            date_counter[publish_time] += 1

            # 创建并写入TXT文件，文件名包括日期和编号
            file_name = f'{publish_time}_{date_counter[publish_time]}'
            output_file_name = os.path.join(output_dir, f'{file_name}.txt')

            with open(output_file_name,'w', encoding='utf-8-sig') as txtfile:
                txtfile.write(text_content)

            print(f'已爬取并保存：{output_file_name}')

            # 更新记录位置
            current_row = index

            # 每爬取一次记录位置，将其保存到记录文件中
            with open(record_file_path, 'w') as record_file:
                record_file.write(str(current_row))
        else:
            print(f'无法访问URL：{url}')
