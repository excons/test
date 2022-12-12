import csv
import datetime
import json
import logging
import sys
import time
from encodings import utf_8_sig  # 액셀파일에서 한글깨질때

import azure.functions as func
import requests
from bs4 import BeautifulSoup

sys.path.append('./')

def main(mytimer: func.TimerRequest, tablePath:func.Out[str]) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    tags1 = finance()
    
    title = "주유소이름	최저가".split("\t")
    data__oil1 = []
    for i, tags in enumerate(tags1):
        data_oil = {
            "주유소 이름": tags[0],
            "최저가": tags[1],
            "RowKey": time.time() 
        }
        data__oil1.append(data_oil)
    # print("data_oil1")
    
    tablePath.set(json.dumps(data__oil1))



def finance():
	url = 'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query=%EC%A3%BC%EC%9C%A0%EC%86%8C'

	filename = '기름.csv'
	f = open(filename, 'w', encoding='utf-8-sig', newline='')
	writer = csv.writer(f)

	# table
	res = requests.get(url)
	soup = BeautifulSoup(res.text, 'lxml')

	# rows 가져오기
	for page in range(0, 5):
		res = requests.get(url)
		res.raise_for_status()
		soup = BeautifulSoup(res.text, 'lxml')
		data_results = []
		try:
			data_rows = soup.find('div', attrs={'class':'place-app-root place_on_pcnx'}).find('ul').find_all('li')
			for row in data_rows:
				columns = row.find('a', class_='BCY5v')
				if len(columns) <= 1 : continue
				data = [column.get_text().strip() for column in columns]
                #print(data)
				data_results.append(data)
				writer.writerow(data)
				print(data_results)
		except IndexError:
			pass
		return data_results