###Edge-Impulse에서 export한 json 데이터를 하나의 csv 파일로 만들어준다

import json
import glob
from datetime import datetime
import csv
import time

import pandas as pd

start = time.time()  # start time
print('Start conversion, json to csv')

# Place your JSON data in a directory named 'data/'
src = "data/"
data = []

# Change the glob if you want to only look through files with specific names
files = glob.glob('data/*', recursive=True)

# Loop through files
cnt = 0
err_cnt = 0
for single_file in files:
    cnt += 1
    title = str({single_file}).split(".")
    label = title[0][7:]

    with open(single_file, 'r') as f:

        # Use 'try-except' to skip files that may be missing data
        try:
            json_file = json.load(f)
            print(f'Converting {single_file}')

            for dataTuple in json_file['payload']['values']:
                temp = []
                temp.extend([
                    cnt,
                    label,
                    dataTuple[0],
                    dataTuple[1],
                    dataTuple[2],
                    dataTuple[3],
                    dataTuple[4],
                    dataTuple[5],
                ])
                data.append(temp)

        except KeyError as e:
            print(e)
            err_cnt += 1
            print(f'Skipping {single_file}')

# Sort the data
# data.sort()

# Add headers
data.insert(0, ['dataId', 'label', 'accX', 'accY', 'accZ', 'gyroX', 'gyroY', 'gyroZ'])

# Export to CSV.
# Add the date to the file name to avoid overwriting it each time.
today = datetime.today().strftime("%Y-%m-%d")
csv_filename = f'{today}_6axis_data.csv'
with open(csv_filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(data)

print(f"Updated CSV, {cnt} json files converted, {err_cnt} files skipped")
print("total time :", round(float(time.time() - start), 2))

# read CSV by pandas
df = pd.read_csv(csv_filename, encoding='utf8', low_memory=False)
pd.set_option('display.max_columns', None)
print(df)
