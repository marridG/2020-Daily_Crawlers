import os, shutil, time
from datetime import datetime
import re
from bs4 import BeautifulSoup
import urllib
from urllib import request
from urllib.parse import quote
import string
from lxml.html import fromstring
import html2text
import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT = "https://zhiyuan.sjtu.edu.cn/"
NAME_LIST_URL = "https://zhiyuan.sjtu.edu.cn/articles/625"
OUTPUT_DES_ROOT = r"...\20200422 Zhiyuan Namelist\data"
TIME_STAMP = datetime.now().strftime("%Y%m%d")  # e.g. 20200422
OUTPUT_DES_FOLDER = "致远学院学生名册 - " + TIME_STAMP  # e.g. 致远学院学生名册 - 20200422
SAVE_PAGE = False
SLEEP_INTERVAL = 0.1  # seconds
DEBUG_MODE = False  # True


def init():
    if DEBUG_MODE:
        print("Initiating ...")
    os.chdir(OUTPUT_DES_ROOT)
    if os.path.exists(OUTPUT_DES_FOLDER):
        while 1:
            try:
                shutil.rmtree(OUTPUT_DES_FOLDER)
                if DEBUG_MODE:
                    print("\t Previous Destination Folder Deleted")
                time.sleep(SLEEP_INTERVAL)
                break
            except:
                time.sleep(0.5)
    while 1:
        try:
            os.mkdir(OUTPUT_DES_FOLDER)
            time.sleep(SLEEP_INTERVAL)
            break
        except:
            time.sleep(0.5)
    os.chdir(OUTPUT_DES_FOLDER)
    if DEBUG_MODE:
        print("\t Destination Folder Initiated and Accessed\n\tInitiated")
    else:
        print("Initiated")


def loose_decode(content):
    return content.decode("utf8", "ignore")


def url_relative_to_absolute(url):
    return ROOT + url if url else None


def get_page_list():
    """
    :return: page_list      <list> of <list>[<str>name_list_url, <str>major, <int>year]
    """
    if DEBUG_MODE:
        print("Fetching List of Name List Pages ...")
    _page = urllib.request.urlopen(NAME_LIST_URL)
    page = loose_decode(_page.read())
    if DEBUG_MODE:
        print("\tRoot Read")

    soup = BeautifulSoup(page, features="html.parser")

    nm_lst_refs = soup.select(".page-body > p > a")
    if DEBUG_MODE:
        print("\tPage Parsed")

    page_list = []  # [<str>url, <str>major, <int>year]
    for a_a in nm_lst_refs:
        _url = a_a["href"]
        _url_sp = _url.split("/")
        _year = int(_url_sp[2])  # OR? a_a.string.split("级")[0]  # OR a_a.text...
        _major = _url_sp[3]
        page_list.append([url_relative_to_absolute(_url), _major, _year])
    if not len(nm_lst_refs) == len(page_list):
        exit(1)
    if DEBUG_MODE:
        print("\tPage List Fetched")
    else:
        print("List of Name Lists  Pages Fetched")

    return page_list


def download_local(page_read, filename, log=None):  # page_read: <byte>
    open(filename, "wb").write(page_read)
    if log and DEBUG_MODE:
        print("\t%s Saved" % log)


def fetch_single_info(q_id, major, year, _idx, _nm):
    """
    :param q_id:    # of namelist in the queue
    :param _idx:    # in the namelist
    :param _nm      web-object of a student
    :return:
        status      0 if nothing to be added, -1 if to add, 1 if success
        temp        <list> of info. [name, description, profile_name]
    """
    _info = _nm.select("td")
    temp = []
    name, description, profile = None, None, None

    # fetching text: name, description
    try:
        _text = _info[1]
        name = _text.select("h3")[0].text.strip()
        try:
            _description = _text.select("div > p")[0].text
        except:
            _description = _text.select("div")[0].text
        # description = fromstring(_description).text_content() # <br> => ' '
        description = html2text.html2text(_description).strip()
        if not description:
            description = "EMPTY_DESCRIPTION"
        temp.extend([name, description])
    except Exception as e:
        print("[ERROR] #%d-%d Parsing Text Failed: %s" % (q_id, _idx, e))
        if name:  # "description" cannot be None; if name==None, continue
            temp.extend([name, "ERROR_DESCRIPTION", "NULL"])
        else:
            return 0, None

    # fetching profile
    try:
        _profile = _info[0]
        profile = url_relative_to_absolute(_profile.select("img")[0]["src"])
        filename = "%s %s #%d %s.jpg" % (major, year, _idx + 1, name)
        download_local(page_read=urllib.request.urlopen(profile).read(),
                       filename=filename, log=None)
        temp.append(filename)
    except Exception as e:
        print("[ERROR] #%d-%d Parsing Profile Source Failed: %s" % (q_id, _idx, e))
        if profile:  # error when/after downloading
            temp.append("ERROR_PROFILE_DOWNLOADING@" + profile)
        else:  # error when parsing
            temp.append("ERROR_PROFILE_PARSING")
        return -1, temp

    return 1, temp


def fetch_stu_info(q_id, page_info):  # [<str>url, <str>major, <int>year]
    """
    :param q_id:            # in the fetching queue
    :param page_info:       <list>[name_list_url, major, year]
    :return:
        info = []           <list> of <list>[name, description, profile_name]
        status = [major, year, success, parsed, altogether, count_text]
            major:          <str>
            year:           <int>
            success:        <int> number of successfully downloaded all info
            parsed:         <int> number of items parsed
            altogether:     <int> shown number of student
            count_text:     <str> sentence showing the student count
    """
    url, major, year = page_info
    if DEBUG_MODE:
        print("#%d\tFetching %s (%s) ..." % (q_id, major, year))

    # handle url with chinese
    # [Reference] https://www.cnblogs.com/wuxiangli/p/9957601.html
    url = quote(url, safe=string.printable)

    # request and read page
    _page = urllib.request.urlopen(url)
    page = loose_decode(_page.read())
    soup = BeautifulSoup(page, features="html.parser")

    # save html page
    if SAVE_PAGE:
        download_local(page.encode(), "%s %d.html" % (major, year), "Name List Page")

    # get total number of students
    _cnt = soup.select("ul.breadcrumb > li.active")[0]
    count_text = _cnt.text
    count = int(_cnt.text.split("共计")[1].split("人")[0].strip())

    # get info details
    _nm_lst = soup.select("table.table.table-hover tr")
    _parsed_len = len(_nm_lst)
    if _parsed_len != count:
        print("\t[ERROR] Count Mismatch: %d out of %d" % (_parsed_len, count))
    time.sleep(SLEEP_INTERVAL)

    info = []  # <list> of <list>[name, description, profile_name]
    _suc_cnt = 0
    if DEBUG_MODE:
        for _idx, _nm in enumerate(tqdm(_nm_lst)):
            _suc, _info = fetch_single_info(q_id, major, year, _idx, _nm)
            info.append(_info)
            _suc_cnt += int(1 == _suc)
    else:
        for _idx, _nm in enumerate(_nm_lst):
            _suc, _info = fetch_single_info(q_id, major, year, _idx, _nm)
            info.append(_info)
            _suc_cnt += int(1 == _suc)

    time.sleep(SLEEP_INTERVAL)
    if DEBUG_MODE:
        print("\t[%d/%d/%d] Suc/Par/Alt" % (_suc_cnt, _parsed_len, count))

    return info, [major, year, _suc_cnt, _parsed_len, count, count_text]


def info_to_excel(cols, info, status, confi, src):
    """
    :param cols         DtaFrame object(like <list>) columns of the sheet
                ["方向", "级", "姓名", "个人简介", "头像路径", "Suc/Par/Alt", "可信", "说明", "源"])
    :param info         <list> of <list>[name, description, profile_name]
    :param status       <list>[major, year, success, parsed, altogether, count_text]
    :param confi        <bool> indicating whether Success, Parsed and Altogether Counts are the same
    :param src          <str> name list source
    :return: df         DataFrame object, containing the recently added info(rows)
    """
    if (not info) or (not status) or (not src):
        return None

    # generating data
    rows = np.array(info, dtype=str)  # [name, description, profile_name]
    rows = np.insert(rows, 0, axis=1, values="%d" % status[1])  # [year, name, description, profile_name]
    rows = np.insert(rows, 0, axis=1, values="%s" % status[0])  # [major, year, name, description, profile_name]
    rows = np.insert(rows, rows.shape[1], axis=1, values="%d/%d/%d" % (
        status[2], status[3], status[4]))  # [major, year, name, description, profile_name, S/P/A]
    rows = np.insert(rows, rows.shape[1], axis=1,
                     values="%r" % confi)  # [major, year, name, description, profile_name, S/P/A, confidence]
    rows = np.insert(rows, rows.shape[1], axis=1,
                     values="%s" % status[
                         5])  # [major, year, name, description, profile_name, S/P/A, confidence, count_text]
    rows = np.insert(rows, rows.shape[1], axis=1,
                     values="%s" % src)  # [major, year, name, description, profile_name, S/P/A, confidence, count_text, source]
    # print(rows[0, :])

    if 1 == len(info):  # [1, 2, 3] will become [[1], [2], [3]] in DF
        df = pd.DataFrame(rows).T
        df.columns = cols
        if DEBUG_MODE:
            print("\tDataFrame Generated")
        return df

    df = pd.DataFrame(rows, columns=cols)
    if DEBUG_MODE:
        print("\tDataFrame Generated")
    return df


if __name__ == "__main__":
    start = datetime.now()
    init()
    page_list = get_page_list()

    print("Start Fetching Flow: %d in Total" % (len(page_list)))
    xlsx = pd.DataFrame(columns=["方向", "级", "姓名", "个人简介",
                                 "头像文件", "Suc/Par/Alt", "可信", "说明", "源"])
    accomplish = np.zeros(3).astype(int)  # success, parsed, altogether
    errors = []  # major, year, success, parsed, altogether
    for idx, page_info in enumerate(tqdm(page_list)):
        # for idx, page_info in enumerate(page_list):
        # page_info: <list> of <list>[<str>name_list_url, <str>major, <int>year]

        info, status = fetch_stu_info(idx + 1, page_info)
        # info: <list> of <list>[name, description, profile_name]
        # status: <list>[major, year, success, parsed, altogether, count_text]

        confidence = (status[2] == status[3]) and (status[3] == status[4])
        accomplish = accomplish + np.array(status[2:5])
        if not confidence:
            errors.append(page_info[1:].extend(status[2:5]))

        df = info_to_excel(xlsx.columns, info, status, confidence, page_info[0])
        xlsx = pd.concat([xlsx, df], ignore_index=True)
        if DEBUG_MODE:
            print("\tDataFrame Merged")

    xlsx.to_excel("0 %s.xlsx" % OUTPUT_DES_FOLDER, sheet_name=TIME_STAMP, index_label="No.")

    # Report
    print("\n\n========================================")
    print("================ REPORT ================\n")
    total_lst_cnt = len(page_list)
    error_lst_cnt = len(errors)
    print("[Execution]\t\t%.2f seconds\n" % ((datetime.now() - start).seconds))
    print("[Fetched]\t\t%d Name Lists\n" % (total_lst_cnt))
    print("[Suc/Par/Alt]\t%d/%d/%d\n" % (accomplish[0], accomplish[1], accomplish[2]))
    print("[Mismatch-Free]\t%d out of %d\n" % (total_lst_cnt - error_lst_cnt, total_lst_cnt))
    if errors:
        print("[Mismatches]")
        for err in errors:
            print("\t%s(%d): %d/%d/%d" % (err[0], err[1], err[2], err[3], err[4]))
    else:
        print("[Mismatches]\tNONE")

    print("\n========================================")
    print("================= END ==================\n")
