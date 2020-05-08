import os
import shutil
from datetime import datetime
import logging
import json
from logging.handlers import RotatingFileHandler
from tqdm import tqdm
import urllib.request
import re
from bs4 import BeautifulSoup

URL_ROOT = "http://gs.cyscc.org/"

# --- FILE_ROOT             <folder>    ** make sure path exists **
#  |--- FILE_CACHE_PATH     <folder>    to be deleted when successfully terminated
#  |--- FILE_DES_ROOT       <folder>    root of crawled results
#    |--- FILE_DES_CERT     <folder>    stores the sample certificates
#    |--- FILE_DECL_NAME    <file>      declarations from the source
#    |--- FILE_RES_NAME     <file>      result file, in json format
#    |--- FILE_LOG_NAME     <file>      log file
#    |--- FILE_NL_SRC_NAME  <file>      "cache" like, contains all the sources of name lists
FILE_ROOT = ".../202005 High School Rewards Crawler/data/"
FILE_DES_ROOT = "全国青少年科技竞赛获奖名单 - " + datetime.now().strftime("%Y%m%d") + "/"
FILE_DECL_NAME = "Declaration.txt"
FILE_DES_CERT = "Sample Certificates/"
FILE_RES_NAME = "Name List.json"
FILE_LOG_NAME = "Log.txt"
FILE_NL_SRC_NAME = "Name Lists Source.json"
FILE_CACHE_PATH = "cache_" + datetime.now().strftime("%Y%m%d%H%S") + "/"

TARGET_SAMPLE_CERT = True  # whether to crawl the sample certificates
LESS_CONSOLE_LOG = True  # whether to show less debug logs in console


def url_rel_to_abs(_url):
    """
    :param _url:  <str> relative url
    :return:      <str> absolute url
    """
    return URL_ROOT + _url if _url else None


def strip_string(_str):
    if not _str:
        return ""
    text = _str.strip()
    text = text.replace(u"\u00A0", "").replace(u"\u0020", "").replace(u"\u3000", "")
    # text = re.sub(' {2,}', ' ', text)
    text = re.sub('\\n{2,}', '\n', text)
    text = re.sub('\\t', ' ', text)
    return text


def chn_string(_str):
    if not _str:
        return None
    text = _str.encode()
    text = text.decode("utf8", "ignore")
    return text


def create_logger():
    log_path = os.path.join(FILE_DES_ROOT, FILE_LOG_NAME)
    # Create Logger
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)
    # Create Handler
    # ConsoleHandler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # File Handler
    file_handler = RotatingFileHandler(log_path, mode='w',
                                       maxBytes=1048576, encoding='UTF-8')
    file_handler.setLevel(logging.NOTSET)
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - @%(name)s === %(levelname)s ===\n%(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    # Add to Logger
    if not LESS_CONSOLE_LOG:
        _logger.addHandler(console_handler)
    _logger.addHandler(file_handler)

    # Optimization
    # logging._srcfile = None  # Information about where calls were made from
    logging.logThreads = 0  # Threading information
    logging.logProcesses = 0  # Process information

    return _logger


def init():
    os.chdir(FILE_ROOT)
    if os.path.exists(FILE_DES_ROOT):
        shutil.rmtree(FILE_DES_ROOT)
    os.mkdir(FILE_DES_ROOT)
    os.mkdir(FILE_CACHE_PATH)
    os.mkdir(os.path.join(FILE_DES_ROOT, FILE_DES_CERT))


def dl():
    shutil.rmtree(FILE_CACHE_PATH)
    if os.path.exists(FILE_CACHE_PATH):
        os.remove(FILE_CACHE_PATH)


def parse_root_page():
    logger.debug("Handling Root URL ...")
    page = urllib.request.urlopen(URL_ROOT).read()
    soup = BeautifulSoup(page, features="html.parser")

    # *** Declaration ***
    logger.debug("\tParsing Declaration ...")
    declaration_wrapper = soup.select("div.pageMain > fieldset.helpInfo")[0]
    _declaration_title = declaration_wrapper.select("legend")[0].text
    declaration_title = strip_string(_declaration_title)  # result
    _declaration_details = declaration_wrapper.select("ul")[0].text
    declaration_details = strip_string(_declaration_details)  # result
    # write declaration
    with open(os.path.join(FILE_DES_ROOT, FILE_DECL_NAME), "w", encoding="utf8") as f:
        f.write("%s\n\n%s" % (declaration_title, declaration_details))
    logger.debug("\t*** Declaration Parsed ***")
    # print(declaration_title)
    # print(declaration_details)

    # *** Events List ***
    # table title, subject > event > name list
    comp_res = {"Fields": ["Fields", "Events Table Title", "Source", "Name Lists"],
                "Events Table Title": "",
                "Source": URL_ROOT,
                "Name Lists": []}
    logger.debug("\tParsing Events List ...")
    comp_wrapper = soup.select("div.pageMain > table.styledTable")[0]
    # events table title
    _comp_title = comp_wrapper.select("th")[0]
    comp_title = strip_string(_comp_title.text)  # JSON result
    comp_res["Events Table Title"] = comp_title
    logger.debug("\t\tEvents Table Title Parsed")
    # events
    logger.debug("\t\tParsing Events Table ...")
    _comps = comp_wrapper.select("td")
    _cnt_comp_sbj, _cnt_comp_comp, _cnt_comp_nl = -1, -1, -1
    _comp_crt_sbj, _comp_crt_comp = "", ""
    for _comp in _comps:
        _attrs_comp = _comp.attrs.keys()
        if "rowspan" in _attrs_comp:  # subject
            _comp_crt_sbj = strip_string(_comp.text)
            _cnt_comp_sbj += 1
            _cnt_comp_comp, _cnt_comp_nl = 0, 0
            logger.debug("\t\t\tNew Subject: %s" % _comp_crt_sbj)
        elif "align" in _attrs_comp:  # event
            _comp_crt_comp = strip_string(_comp.text)
            _cnt_comp_comp += 1
            _cnt_comp_nl = 0
            logger.debug("\t\t\t\tNew Event: %s" % _comp_crt_comp)
        else:  # namelist
            if "明天小小科学家" in _comp_crt_comp:  # Special Case
                _c_wrapper = _comp.select("a")
                for _c in _c_wrapper:
                    _c_title = strip_string(_c.text)
                    _c_href = url_rel_to_abs(_c["href"])
                    comp_res["Name Lists"].append({
                        "subject": _comp_crt_sbj, "event": _comp_crt_comp,
                        "name list": _c_title, "link": _c_href})
                    _cnt_comp_nl += 1
                    logger.debug("\t\t\t\t\t#%d NameList Detected" % _cnt_comp_nl)
                continue

            try:
                _c_title = strip_string(_comp.text)
                _c_href = url_rel_to_abs(_comp.select("a")[0]["href"])
            except IndexError:  # empty table cell
                logger.debug("\t\t\t\t\t#%d Skipped, Empty Table Cell" % _cnt_comp_nl)
            else:
                comp_res["Name Lists"].append({
                    "subject": _comp_crt_sbj, "event": _comp_crt_comp,
                    "name list": _c_title, "link": _c_href})
                _cnt_comp_nl += 1
                logger.debug("\t\t\t\t\t#%d NameList Detected" % _cnt_comp_nl)
    # write comptitions name lists info
    with open(os.path.join(FILE_DES_ROOT, FILE_NL_SRC_NAME), "w", encoding="utf8") as f:
        json.dump(obj=comp_res, fp=f, indent=4, ensure_ascii=False)
    logger.debug("\t\t*** Events Table Parsed ***")
    logger.debug("\t*** Events List Parsed ***")
    if LESS_CONSOLE_LOG:
        print("Root Page - Events List Parsed")

    # *** Sample Certificates ***
    if not TARGET_SAMPLE_CERT:
        logger.debug("*** Root URL Handled ***")
        return
    cert_res = {"Fields": ["Fields", "Sample Certificates Title", "Certificates", "Failed"],
                "Sample Certificates Title": "",
                "Certificates": [],
                "Failed": []}
    logger.debug("\tParsing & Saving Sample Certificates ...")
    cert_wrapper = soup.select("div.pageMain > table.styledTable")[1]
    # certificate title
    _cert_title = cert_wrapper.select("th")[0]
    cert_title = strip_string(_cert_title.text)  # JSON result
    cert_res["Sample Certificates Title"] = cert_title
    logger.debug("\t\tSample Certificates Table Title Parsed")
    # certificates
    logger.debug("\t\tSaving Sample Certificates ...")
    _certs = cert_wrapper.select("td")
    _cnt_cert = 0
    for _cert in _certs:
        try:
            _c = _cert.select("a")[0]
            _c_title = _c["title"]
            _c_href = url_rel_to_abs(_c["href"])
            _c_fn = "%s-%s%s" % (cert_title, _c_title, _c_href[_c_href.rfind("."):])
            _c_img = urllib.request.urlopen(_c_href).read()
            open(os.path.join(FILE_DES_ROOT, FILE_DES_CERT, _c_fn), "wb").write(_c_img)
        except IndexError:  # empty table cell
            logger.debug("\t\t\t#%d Skipped, Empty Table Cell" % _cnt_cert)
        except Exception as err:
            cert_res["Failed"].append({"id": _cnt_cert, "error": str(err)})
            logger.error("\t\t\t#%d Certificate Failed" % _cnt_cert)
        else:
            cert_res["Certificates"].append({"id": _cnt_cert, "title": _c_title,
                                             "source": _c_href, "file name": _c_fn})
            logger.debug("\t\t#%d Certificate Done" % _cnt_cert)
        finally:
            _cnt_cert += 1
    # write certificates info
    # with open(os.path.join(FILE_DES_ROOT, FILE_DES_CERT, "0 readme.txt"), "w", encoding="utf8") as f:
    #     f.write("DECLARATION:\nAll Data from %s\n" % URL_ROOT)
    #     f.write("Refer to file \"0 readme.json\" for more details.\n")
    with open(os.path.join(FILE_DES_ROOT, FILE_DES_CERT, "0 readme.json"), "w", encoding="utf8") as f:
        json.dump(obj=cert_res, fp=f, indent=4, ensure_ascii=False)
    logger.debug("\t\t*** Sample Certificates Saved ***")

    logger.debug("\t*** Parsing & Saving Sample Certificates Done ***")
    if LESS_CONSOLE_LOG:
        print("Root Page - Sample Certificates Saved")
    logger.debug("*** Root URL Handled ***")


def crawl_name_list():
    logger.debug("Handling Name Lists ...")
    with open(os.path.join(FILE_DES_ROOT, FILE_NL_SRC_NAME), "r", encoding="utf8") as f:
        _nm_lst_src = json.load(f)
    nm_lst_src = _nm_lst_src["Name Lists"]
    logger.debug("\tName Lists Source Loaded")
    logger.debug("\tCrawling Name Lists ...")
    if LESS_CONSOLE_LOG:
        print("Name Lists Pages - Start Parsing ...")
    for lst_src in tqdm(nm_lst_src):
        redirected_link = None
        fn = "%s-%s-%s.json" % (lst_src["subject"], lst_src["event"], lst_src["name list"])
        page = urllib.request.urlopen(lst_src["link"]).read()
        soup = BeautifulSoup(page, features="html.parser")

        # redirect, select "all" for area
        if "<ul class=\"areaList\">" in page.decode():
            _redirected_link = soup.select("ul.areaList > li > a")[0]
            redirected_link = url_rel_to_abs(_redirected_link["href"])
            if "全部" not in _redirected_link.text:
                logger.error("TODO")
            page = urllib.request.urlopen(redirected_link).read()
            soup = BeautifulSoup(page, features="html.parser")

        lst_res = {"Fields": ["Fields", "Names Items"], "Names Items": []}
        # parse page
        wrapper = soup.select("div.pageMain > table.styledTable > tbody > tr")[1:]
        for _item in wrapper:
            item = _item.select("td")
            name = item[0].text
            school = item[1].text
            area = item[2].text
            prize = item[3].text
            lst_res["Names Items"].append({
                "Events Table Title": _nm_lst_src["Events Table Title"],
                "Subject": lst_src["subject"],
                "Event": lst_src["event"],
                "Name List": lst_src["name list"],
                "Link": lst_src["link"], "Redirected Link": redirected_link,
                "name": name, "school": school, "area": area, "prize": prize})
        with open(os.path.join(FILE_CACHE_PATH, fn), "w", encoding="utf8") as f:
            json.dump(obj=lst_res, fp=f, indent=4, ensure_ascii=False)
    logger.debug("*** Name Lists Crawled ***")


def merge_as_json():
    logger.debug("Merging Caches ...")
    res = {"Fields": ["Fields", "Items"], "Itmes": []}
    for cache_file in os.listdir(FILE_CACHE_PATH):
        with open(os.path.join(FILE_CACHE_PATH, cache_file), "r", encoding="utf8") as f:
            cache = json.load(f)
        for item in cache["Names Items"]:
            res["Itmes"].append({
                "Events Table Title": item["Events Table Title"],
                "Subject": item["Subject"],
                "Event": item["Event"],
                "Name List": item["Name List"],
                "Link": item["Link"], "Redirected Link": item["Redirected Link"],
                "Name": item["name"],
                "School": item["school"], "Area": item["area"], "Prize": item["prize"]})
        logger.debug("\tMergd %d Items in File %s" % (len(cache["Names Items"]), cache_file))
    with open(os.path.join(FILE_DES_ROOT, FILE_RES_NAME), "w", encoding="utf8") as f:
        json.dump(obj=res, fp=f, indent=4, ensure_ascii=False)
    if LESS_CONSOLE_LOG:
        print("Local - Caches Merged")
    logger.debug("*** Caches Merged ***")


init()
logger = create_logger()
parse_root_page()
crawl_name_list()
merge_as_json()
dl()
