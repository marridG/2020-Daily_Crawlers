import os
import sys
import shutil
from tqdm import tqdm
import urllib.request
import urllib.error
import socket
from datetime import datetime
import numpy as np
import time

OUTPUT_DES_ROOT = r"...\202004 MCM_ICM Results\MCM_ICM"
TIME_STAMP = datetime.now().strftime("%Y%m%d")  # e.g. 20200422
OUTPUT_DES_FOLDER = "2020 MCM_ICM 获奖证书-" + TIME_STAMP  # e.g. 2020 MCM_ICM 获奖证书-20200422"
LOG_FILE = "0 log.txt"
DEBUG_MODE = True
MAX_ATTEMPTS = 1
MIN = 2000000
MAX = 2099999


class Logger(object):
    # Reference
    #   https://blog.csdn.net/a1379478560/article/details/91405653
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, mode='a', encoding='utf-8')

    def write(self, message):
        # self.terminal.write(message)
        self.log.write(message)
        self.flush()

    def flush(self):
        self.log.flush()


os.chdir(OUTPUT_DES_ROOT)
if os.path.exists(OUTPUT_DES_FOLDER):
    while 1:
        try:
            shutil.rmtree(OUTPUT_DES_FOLDER)
            if DEBUG_MODE:
                print("\tPrevious Destination Folder Deleted")
            time.sleep(0.1)
            break
        except:
            time.sleep(0.5)
while 1:
    try:
        os.mkdir(OUTPUT_DES_FOLDER)
        time.sleep(0.1)
        break
    except:
        time.sleep(0.5)
os.chdir(OUTPUT_DES_FOLDER)
if DEBUG_MODE:
    print("\tDestination Folder Initiated and Accessed\n\tInitiated")

sys.stdout = Logger(LOG_FILE)
# socket.setdefaulttimeout(10)  # seconds

start = datetime.now()

downloaded_teams = []
non_exist_teams = []
timed_out_teams = []
for team_id in tqdm(range(MIN, MAX + 1)):
    url = "http://comap-math.com/mcm/2020Certs/%d.pdf" % team_id

    response, content = None, None
    attempts = 0
    while attempts <= MAX_ATTEMPTS:
        try:
            response = urllib.request.urlopen(url, timeout=5)
            content = response.read()
            break
        except (urllib.error.HTTPError, urllib.error.URLError) as err:
            if DEBUG_MODE:
                print("[ERROR] %d: %s" % (team_id, err))
            non_exist_teams.append(team_id)
            break
        except socket.timeout as err:
            attempts += 1
            if 5 == attempts:
                timed_out_teams.append(team_id)
                if DEBUG_MODE:
                    print("[ERROR] %d: %s" % (team_id, err))
            continue

    if not content:
        continue

    open("%d.pdf" % team_id, "wb").write(content)
    downloaded_teams.append(team_id)
    if DEBUG_MODE:
        print("%d Downloaded" % team_id)

print("\n\n========================================")
print("================ REPORT ================\n")
total_team_cnt = MAX - MIN
downloaded_team_cnt = len(downloaded_teams)
non_exist_team_cnt = len(non_exist_teams)
timed_out_team_cnt = len(timed_out_teams)
print("[Execution]\t\t%.2f seconds\n" % (datetime.now() - start).seconds)
print("[Counts]\t\t\t"
      "Total:\t\t%d\n\t\t\t"
      "Downloaded:\t%d\n\t\t\t"
      "404:\t\t%d\n\t\t\t"
      "Timed Out:\t%d" % (
          total_team_cnt,
          downloaded_team_cnt,
          non_exist_team_cnt,
          timed_out_team_cnt))
if downloaded_team_cnt:
    print("[Downloaded]\n\t", np.array(downloaded_teams), "\n")
else:
    print("[Downloaded]\t\tNone\n")
if non_exist_team_cnt:
    print("[Non-Existence]\n\t", np.array(non_exist_teams), "\n")
else:
    print("[Non-Existence]\t\tNone\n")
if timed_out_team_cnt:
    print("[Timed Out]\n\t", np.array(timed_out_teams), "\n")
else:
    print("[Timed Out]\t\tNone\n")
# print()

print("========================================")
print("================= END ==================\n")

time.sleep(10)
