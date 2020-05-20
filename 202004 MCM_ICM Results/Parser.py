import os
import re
import shutil
import time
from datetime import datetime
import urllib.request
import urllib.error
import socket
import copy
import json
import logging
from logging.handlers import RotatingFileHandler
import cv2
import fitz
import pytesseract
from PIL import Image
from tqdm import tqdm
import numpy as np


def create_logger(log_path="log.txt", less_log=False):
    # remove log file if exists
    if os.path.exists(log_path):
        os.remove(log_path)

    # Create Logger
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)
    # Create Handler
    # ConsoleHandler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # File Handler: 1M=1048576, 5M=5242880
    file_handler = RotatingFileHandler(log_path, mode='w',
                                       maxBytes=5242880, backupCount=200,
                                       encoding='UTF-8')  # MAX: 5M * 200
    file_handler.setLevel(logging.NOTSET)
    # Formatter
    formatter = logging.Formatter('%(asctime)s - @%(name)s === %(levelname)s ===\n%(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    # Add to Logger
    if not less_log:
        _logger.addHandler(console_handler)
    _logger.addHandler(file_handler)

    # Optimization
    # logging._srcfile = None  # Information about where calls were made from
    logging.logThreads = 0  # Threading information
    logging.logProcesses = 0  # Process information

    return _logger


class PrizeParser:
    def __init__(self, root, files_path="files/", templates_path="templates/", logger=None,
                 delete_cache=True, cache_img_stream=True,
                 report_filename="report", result_filename="result.json",
                 _online_max_conti_err=1000, _online_timeout=5, _online_max_attempts=2):
        """
        :param root: (Required)     <str>   Default workspace: where required files are stored, etc.
        :param files_path:          <str>   (relative to "root") local path where PDF(s) are/is stored
                                            [DEFAULT] "files/"
        :param templates_path:      <str>   (relative to "root") local path where REQUIRED templates are stored
                                            [DEFAULT] "templates/"
        :param logger:              <logging.RootLogger>
                                            [DEFAULT] None (to be created later)
        :param delete_cache:        <bool>  Whether to delete cache files after execution
                                            [DEFAULT] True
                                            False for debug only, not recommended
        :param cache_img_stream:    <bool>  Whether to use stream to pass cache images
                                            [DEFAULT] True (Recommended)
                                            True    recommended for machines of high computational capabilities
                                            False   recommended for machines of high I/O performance
        :param report_filename:     <str>   (relative to "root") local path where report file is stored
                                            [DEFAULT] "report"
        :param result_filename:     <str>   (relative to "root") local path where result json file is stored
                                            [DEFAULT] "result.json"
        :param _online_max_conti_err <int>  for online parser only, maximum number of continuous errors
                                            [DEFAULT] 1000
        :param _online_timeout      <float> for online parser only, timeout in seconds
                                            [DEFAULT] 5
        :param _online_max_attempts <int>   for online parser only, max failure attempts
                                            [DEFAULT] 2
        """
        # [VALIDATION] root
        if not os.path.exists(root):
            exit("[ERROR] Assigned Root Path Non-Existent")

        # [PATH] backup & set workspace
        self.default_workspace = os.getcwd()
        self.root = root

        # [FILE/OBJECT] create logger
        self._logger_from_default_or_src = bool(logger is not None)
        self.logger = self.initiate_logging() if not self._logger_from_default_or_src else logger

        # [OPERATION] Move to Workspace
        os.chdir(self.root)
        self.logger.info("Working at %s" % self.root)

        # [VALIDATION] templates path
        if not templates_path:
            msg = "[ERROR] Assigned Templates Path Non-Existent %s" % templates_path
            self.logger.critical(msg)
            exit(msg)

        # [PATH] pdf files
        self.files_path = files_path

        # [PATH] templates
        self.templates_path = templates_path
        self.templates_names = os.listdir(self.templates_path)
        self.templates, self.templates_shape = self.initiate_templates()

        # [PATH] cache
        self.cache_path = "cache_" + datetime.now().strftime("%Y%m%d%H%M%S") + "/"
        os.mkdir(self.cache_path)
        self.cache_result_file = open(os.path.join(self.cache_path, "_cache_result.txt"), "w+")

        # [KWARGS] kwargs
        self.delete_cache = delete_cache  # "False" for DEBUG only
        self.cache_img_stream = cache_img_stream  # using stream for cropped image if True else False
        self.report_filename = report_filename  # File Initialization Recommended
        self.result_filename = result_filename  # File Initialization Recommended
        self._online_max_conti_err = _online_max_conti_err  # for online parser only
        self._online_timeout = _online_timeout  # for online parser only
        self._online_max_attempts = _online_max_attempts  # for online parser only
        # file initialization
        for _file in [self.report_filename, self.result_filename]:
            if os.path.exists(_file):
                os.remove(_file)

        # set PDF -> IMG resize/rotation param
        zoom_x, zoom_y, rotation_angle = 5, 5, 0
        self.pdf_img_trans = fitz.Matrix(
            zoom_x, zoom_y).preRotate(rotation_angle)

        # parsed result info sample
        self.res_info_dict = {"team_number": 0000000,
                              "student1": "", "student2": "", "student3": "",
                              "advisor_type": "", "advisor": "",
                              "school": "",
                              "prize": ""}

        # for report
        self.file_cnt, self.suc_cnt = 0, 0
        self.failed_list = []
        self.start_time = datetime.now()

        self.logger.debug("Parser Class Initiated")
        self.report_init()

    def initiate_logging(self, log_path="log"):
        # Create Logger
        _logger = logging.getLogger()
        _logger.setLevel(logging.DEBUG)
        # Create Handler
        # ConsoleHandler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        # File Handler
        file_handler = RotatingFileHandler(os.path.join(self.root, log_path),
                                           mode='w', maxBytes=1048576, backupCount=200,
                                           encoding='UTF-8')  # 1M * 200
        file_handler.setLevel(logging.NOTSET)
        # Formatter
        formatter = logging.Formatter('%(asctime)s - @%(name)s === %(levelname)s ===\n%(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        # Add to Logger
        _logger.addHandler(console_handler)
        _logger.addHandler(file_handler)

        # Optimization
        # logging._srcfile = None  # Information about where calls were made from
        logging.logThreads = 0  # Threading information
        logging.logProcesses = 0  # Process information

        return _logger

    def initiate_templates(self):
        templates = []
        templates_shape = []  # y * x (e.g. 60,197)
        for tn in self.templates_names:
            template = cv2.imread(os.path.join(self.templates_path, tn), 0)
            templates.append(template)
            templates_shape.append(template.shape)
        self.logger.debug("Parser Class Initiating: Templates Read")
        return templates, templates_shape

    def report_init(self):
        out_str = "\n==============================\n" \
                  "[START AT]\t%s\n" \
                  "[WORKING]\t%s\n" \
                  "[FILES]\t\t%s\n" \
                  "[TEMPLATES]\t%s\n" \
                  "[CACHE]\t\t%s\n" \
                  "[LOGGER]\t%s\n" \
                  "[KWARGS]\n" \
                  "\tdelete cache:\t\t%s\n" \
                  "\tstream image cache:\t%s\n" \
                  "\treport filename:\t%s\n" \
                  "\tresult filename:\t%s\n" \
                  "[ONLINE ONLY KWARGS]\n" \
                  "\tmax conti err cnt:\t%d\n" \
                  "\ttimeout:\t\t\t%d\n" \
                  "\tmax attempts:\t\t%d\n" \
                  "==============================\n\n" \
                  % (self.start_time,
                     self.root,
                     self.files_path if self.files_path else "NONE",
                     self.templates_path,
                     self.cache_path,
                     "DEFAULT" if self._logger_from_default_or_src else "ASSIGNED",
                     str(self.delete_cache).upper(),
                     str(self.cache_img_stream).upper(),
                     self.report_filename,
                     self.result_filename,
                     self._online_max_conti_err, self._online_timeout, self._online_max_attempts)
        print(out_str)
        open(self.report_filename, "w", encoding="utf8").write(out_str)

    def report_exec(self, local=False, online=False):
        if not local ^ online:
            msg = "Ambiguous Parser: Local=%r, Online=%r" % (local, online)
            self.logger.critical(msg)
            exit(msg)

        if local:
            out_str = "\n*** Local Parser Executed***\n"
        else:  # online
            out_str = "\n*** Online Parser Executed ***\n"
        open(self.report_filename, "a", encoding="utf8").write(out_str)

    def report_del(self):
        out_str = "\n\n=== [TIME EXECUTED] ===\n" \
                  "\t%s\n" \
                  "\n=== [TOTAL] ===\n" \
                  "\t%d Teams/PDF(s)" % (datetime.now() - self.start_time, self.file_cnt)
        if 0 != self.file_cnt:
            _failed_cnt = len(self.failed_list)
            out_str = "%s\n" \
                      "\n=== [SUCCESS] ===\n" \
                      "\t%d (%.2f%%)\n" \
                      "\n=== [FAILED] ===\n" \
                      "\t%d Teams/PDF(s)\n" \
                      "%s" \
                      % (out_str,
                         self.suc_cnt, self.suc_cnt / self.file_cnt * 100.,
                         _failed_cnt,
                         str(self.failed_list) if _failed_cnt else "")

        print(out_str)
        open(self.report_filename, "a", encoding="utf8").write(out_str)

    def __del__(self):
        self.cache_result_file.close()
        if self.delete_cache:
            shutil.rmtree(self.cache_path)
            if os.path.exists(self.cache_path):
                os.remove(self.cache_path)
        # Parser Class Destructing: Cache Deleted
        os.chdir(self.default_workspace)
        # Parser Class Destructing: Workspace Returned
        # Parser Class Destructed
        time.sleep(0.5)

    def img_to_text(self, img_target):
        """
        OCR image
        :param img_target:  None or:
                            1. if not self.cache_img_stream:
                                <str> the filename (without path) of the image to OCR
                            2. if     self.cache_img_stream:
                                <numpy.ndarray> the data array of the image to OCR
        :return:            <str> the OCRed text after "process" --- remove duplicate " ", "\n"
                            None if "img_target" is None
        """
        if img_target is None:
            self.logger.warning("\tImg OCR Got No Inputs")
            return None

        if not self.cache_img_stream:  # NOT Recommended: not using stream while passing cropped images
            im = Image.open(os.path.join(self.cache_path, img_target))
        else:  # Recommended: using stream while passing cropped images
            im = img_target

        text = pytesseract.image_to_string(im)
        # print(text)
        text = text.strip()
        text = re.sub(' \\n', '\n', text)
        text = re.sub('\\n ', '\n', text)
        text = re.sub(' {2,}', ' ', text)
        text = re.sub('\\n{2,}', '\n', text)
        self.logger.debug("\tImg OCR Done")
        return text

    def pdf_to_image(self, pdf_name=None, pdf_stream=None, fs_team_id=None):
        """
        print Page 0 of pdf to IMG(PNG) and save
        :param pdf_name:    <str> filename (without path) of the PDF file to create a fitz.Document to print to IMG
                            None (default)
        :param pdf_stream:  <b str> binary stream of the PDF to create a fitz.Document to print to IMG
                            None (default)
        :param fs_team_id:  <int> team number, given only when filestream is given
                            None (default)
        :return:            1. if not self.cache_img_stream: <str> the filename of the printed IMG (GrayScale)
                            2. if     self.cache_img_stream: <bytes> data of PNG in bytes of the printed IMG (GrayScale)

        Note:   If either
                    1. either param is given
                    2. both params are given
                , an error will be raised.
        """
        if (not pdf_name) and (not pdf_stream):
            raise PDF2IMGError("Neither Filename or Stream is Given")
        if pdf_name and pdf_stream:
            raise PDF2IMGError("Both Filename and Stream are Given")

        if pdf_name:  # NOT Recommended
            pdf = self.pdf_obj_file(pdf_name)
        else:  # pdf_stream is not None
            pdf = self.pdf_obj_stream(pdf_stream)

        pm = pdf[0].getPixmap(matrix=self.pdf_img_trans, alpha=False)
        if not self.cache_img_stream:  # NOT Recommended: not using stream as input for further cropping
            out_path = self.cache_path
            out_name = pdf_name.split(".")[0] + ".png" if pdf_name else "%d.png" % fs_team_id
            pm.writePNG(os.path.join(out_path, out_name))
            res = out_name
        else:  # Recommended: using stream as input for further cropping
            res = pm.getPNGData()
        pdf.close()

        self.logger.debug("\tPDF Printed To PNG")
        return res

    def pdf_obj_file(self, pdf_name):
        """
        :param pdf_name:    <str> the filename (without path) of the source PDF
        :return:            <fitz.Document object>
        """
        return fitz.open(os.path.join(self.files_path, pdf_name))

    @staticmethod
    def pdf_obj_stream(pdf_stream):
        """
        :param pdf_stream:  <b str> the stream of the source "PDF"
        :return:            <fitz.Document object>
        """
        return fitz.open(stream=pdf_stream, filetype="pdf")

    def crop_img(self, page_img):
        """
        crop the page of the PDF to different categories:
                students, advisor type, advisor, school, prize

        :param page_img:    1. if not self.cache_img_stream:
                                    <str> the filename (without path) of the printed IMG (GrayScale) of the PDF
                            2. if     self.cache_img_stream:
                                    <bytes> data of PNG in bytes of the printed IMG (GrayScale) of the PDF

        :return:            1. if not self.cache_img_stream:
                                    <dict>  {"students":"...",
                                                "advisor":"...", "advisor_type":"..."/None,
                                                "school":"...", "prize":"..."}
                            2. if     self.cache_img_stream: (<*>=<numpy.ndarray>)
                                    <dict>  {"students":<*>,
                                                "advisor":<*>, "advisor_type":<*>/None,
                                                "school":<*>, "prize":<*>}

        Note: if "img_name" is None, an error will be raised
        * if the input image is not GrayScale(RGB/...), notice that OpenCV reads in BGR
        """
        if not page_img:
            raise IMGCropperError("No Input Page IMG")

        if not self.cache_img_stream:  # NOT Recommended: not using stream as input while cropping
            img = cv2.imread(os.path.join(self.cache_path, page_img), cv2.IMREAD_GRAYSCALE)
        else:  # Recommended: using stream as input while cropping
            img = cv2.imdecode(np.frombuffer(page_img, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)

        max_fits = []  # best it locations: x * y [e.g. 1692,752]
        # self.template_shapes: <list> y * x [e.g. 60,197]
        for idx, template in enumerate(self.templates):
            match = cv2.matchTemplate(img, template, cv2.TM_CCOEFF)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)
            # print(max_loc)
            max_fits.append(max_loc)

        # delete "Of"
        _del_as_black = np.where(self.templates[2] < 250)  # y * x
        img[_del_as_black[0] + max_fits[2][1], _del_as_black[1] + max_fits[2][0]] = 255
        # delete "Was Designated As"
        _del_as_black = np.where(self.templates[2] < 250)  # y * x
        img[_del_as_black[0] + max_fits[2][1], _del_as_black[1] + max_fits[2][0]] = 255  # y * x

        # calculating boundaries
        _X = (700, 3800)
        _YMAX = 2200
        _Y = {}  # stores the boundaries
        max_intl = [400, 200, 200, 300]
        # handle case where "with * advisor" missed
        if max_fits[1][1] > max_fits[2][1]:
            cut = max_fits[0][1] + self.templates_shape[0][0] + max_intl[0]
            _Y["students"] = (max_fits[0][1] + self.templates_shape[0][0], cut)
            _Y["advisor"] = (cut, max_fits[2][1])
            _Y["advisor_type"] = None
        else:
            _Y["students"] = (max_fits[0][1] + self.templates_shape[0][0], max_fits[1][1])
            _Y["advisor"] = (max_fits[1][1] + self.templates_shape[1][0], max_fits[2][1])
            _Y["advisor_type"] = (max_fits[1][1], max_fits[1][1] + self.templates_shape[1][0])
        # _Y["school"] = (max_fits[2][1] + self.templates_shape[2][0], max_fits[3][1]) # no deletion "Of"
        _Y["school"] = (max_fits[2][1], max_fits[3][1])
        _Y["prize"] = (max_fits[3][1] + self.templates_shape[3][0], _YMAX)

        # self.create_logger.debug("Created")

        out_imgs = _Y  # using the same <dict> to decrease space usage (boundaries => image name / ndarray)
        out_path = self.cache_path  # for NOT-Recommended Non-Stream Only
        for item in _Y.items():
            if not item[1]:  # None for some advisor_type
                continue
            cropped_img = img[item[1][0]:item[1][1], _X[0]:_X[1]]  # [y, x]

            if not self.cache_img_stream:  # NOT Recommended: not using stream as input while cropping
                out_name = page_img.split(".")[0] + "_" + item[0] + ".png"
                out_imgs[item[0]] = out_name
                cv2.imwrite(os.path.join(out_path, out_name), cropped_img)
            else:  # Recommended: using stream as input while cropping
                out_imgs[item[0]] = cropped_img

        self.logger.debug("\tPage Img Cropped")
        return out_imgs

    def parse_cache_2_get_result_info(self, cropped_imgs):
        """
        main SOLID working function to translate a assigned PDF, given its name
        :param cropped_imgs:    <dict>  {"students":<*>, "advisor":<*>, "advisor_type":<*>/None,
                                            "school":<*>, "prize":<*>}
                        1. if not self.cache_img_stream: <*>=<str>
                        2. if     self.cache_img_stream: <*>=<numpy.ndarray>

        :return: <dict> info of a team (NO team number)
                    {"student1": "", "student2": ""/None, "student3": ""/None,
                        "advisor_type": ""/None, "advisor": "",
                        "school": "", "prize": ""}
        """
        res_info = copy.deepcopy(self.res_info_dict)

        # +++ students names
        _students = self.img_to_text(cropped_imgs["students"])
        students = _students.split("\n")
        st_cnt = len(students)
        if st_cnt > 3 or st_cnt < 1:
            # print(_students, students)
            _error_msg = "Parsing Students Failed: " \
                         "too Many/Few Items (expected 0~3, got %d)" % st_cnt
            raise ParsingError(_error_msg)
        try:
            res_info["student1"] = students[0]
            res_info["student2"] = students[1]
            res_info["student3"] = students[2]
        except IndexError:
            pass

        # +++ advisor name
        advisor = self.img_to_text(cropped_imgs["advisor"]).replace("\n", " ")
        advisor = re.sub(" {2,}", " ", advisor)
        res_info["advisor"] = advisor

        # +++ advisor type
        _advisor_type = self.img_to_text(cropped_imgs["advisor_type"])
        if not _advisor_type:
            advisor_type = None
        elif "Faculty" in _advisor_type:
            advisor_type = "Faculty"
        elif "Student" in _advisor_type:
            advisor_type = "Faculty"
        else:
            try:
                advisor_type = _advisor_type.split()[1]
            except IndexError as err:
                self.logger.warning("[ERROR] Parsing Advisor Type Failed: %s" % err)
                advisor_type = None
        res_info["advisor_type"] = advisor_type

        # +++ school
        school = self.img_to_text(cropped_imgs["school"]).replace("\n", " ")
        school = re.sub(" {2,}", " ", school)
        res_info["school"] = school

        # +++ prize
        prize = self.img_to_text(cropped_imgs["prize"])
        res_info["prize"] = prize

        self.logger.debug("\tResult Information Parsed")
        return res_info

    def remove_used_cache(self, used_files_lst):
        """
        remove cached files (e.g. printed page imgs, cropped imgs, etc.)
        :param used_files_lst: <list> of <str>, the list of the filenames (without path) of the cache files
        """
        if not self.delete_cache:
            return
        for used in used_files_lst:
            if used is not None:  # c.e.g. advisor type might be none
                os.remove(os.path.join(self.cache_path, used))
        self.logger.debug("\tUsed Cache Removed")

    def translate_pdf(self, filename=None, filestream=None, fs_team_id=None):
        """
        main VIRTUAL working function to translate a assigned PDF, given its name
        :param filename:    filename (without path) of the target PDF
                            None (default)
        :param filestream:  <b str> binary stream of the PDF to create a fitz.Document to print to IMG
                            None (default)
        :param fs_team_id:  <int> team number, given only when filestream is given
                            None (default)
        :return:            <dict> info of a team:
                                {"team_number": 0000000, "student1": "", "student2": ""/None, "student3": ""/None,
                                    "advisor_type": ""/None, "advisor": "",
                                    "school": "", "prize": ""}
        Note:   If either
                    1. either param is given
                    2. both params are given
                , an error will be raised here and (not likely) in self.pdf_to_image()
        """
        if not (filename is None) ^ (filestream is None):
            raise PDF2IMGError("Both/Neither Filename, Stream are/is given")

        page_img = self.pdf_to_image(pdf_name=filename, pdf_stream=filestream, fs_team_id=fs_team_id)
        cropped_imgs = self.crop_img(page_img)

        if filename:
            team_number = int(filename.split(".")[0])
        else:
            team_number = fs_team_id

        res_info = self.parse_cache_2_get_result_info(cropped_imgs)
        res_info["team_number"] = team_number

        # Remove the used caches
        if not self.cache_img_stream:  # NOT Recommended: not using stream as input while cropping
            used_files = list(cropped_imgs.values())
            used_files.append(page_img)
            self.remove_used_cache(used_files)

        return res_info

    def update_res_to_cache(self, info):
        """
        store info to cache
        :param info:    <dict> info of a team:
                        {"team_number": 0000000, "student1": "", "student2": ""/None, "student3": ""/None,
                            "advisor_type": ""/None, "advisor": "", "school": "", "prize": ""}
        :return:        <int> length of successfully written string
        """
        try:
            wl = self.cache_result_file.write(str(info))
        except UnicodeEncodeError:
            wl = self.cache_result_file.write(str(info).encode("gbk", 'ignore').decode("gbk", "ignore"))
        self.cache_result_file.write("\n")
        self.cache_result_file.flush()

        self.logger.debug("\tInfo Result Updated to Cache")
        return wl

    def cache_to_json(self):
        """
        read from cache to form json and save it
        """
        # {"team_number": 0000000,  "student1": "", "student2": "", "student3": "",
        #  "advisor_type": "",      "advisor": "",  "school": "",   "prize": ""}
        json_details = {"fields": ["teams counts", "teams numbers",
                                   "student1", "student2", "student3",
                                   "advisor_type", "advisor", "school", "prize"],
                        "teams counts": 0,
                        "teams numbers": [],
                        "info": []}
        self.cache_result_file.seek(0, 0)
        lines = self.cache_result_file.readlines()
        json_details["teams counts"] = len(lines)
        for line in lines:
            info = eval(line)
            json_details["teams numbers"].append(info["team_number"])
            json_details["info"].append(info)

        with open(self.result_filename, "w") as f:
            json.dump(obj=json_details, fp=f, indent=4)

        self.logger.debug("Info Result Updated to JSON")

    def get_files_names(self):
        """
        :return: a list of <str> containing all the filenames in the PDF file directory
        """
        self.logger.debug("Local PDF Filenames Walked")
        return os.listdir(self.files_path)

    def local_parser(self, fl_lst):
        """
        Parse info from local (pre-downloaded) PDFs, and output as JSON
        :param fl_lst:      <list> of <str>, filename (without path) of local PDFs
        """
        print("Running Local Parser ...\n")
        self.report_exec(local=True)
        time.sleep(0.5)

        for file in tqdm(fl_lst):
            if not file.endswith(".pdf"):
                self.logger.warning("Invalid File", file)
                continue
            self.logger.info("Working on %s" % file)
            self.file_cnt += 1

            try:
                info = self.translate_pdf(filename=file, filestream=None, fs_team_id=None)
                self.update_res_to_cache(info)
                self.suc_cnt += 1
            except Exception as err:
                self.failed_list.append(file)
                self.logger.error("[ERROR] %s" % err)
                continue
            self.logger.info("Parser Finished for %s" % file)

        self.cache_to_json()
        self.report_del()

    def request_pdf_stream(self, team_id):
        """
        request source to get the PDF stream
        :param team_id:     <int> team number
        :return:            <b str> file stream
        """
        # url = "http://comap-math.com/mcm/2020Certs/%d.pdf" % team_id
        url = "http://comap-math.com/mcm/2019Certs/%d.pdf" % team_id

        content = None
        attempts = 0
        while attempts <= self._online_max_attempts:
            try:
                response = urllib.request.urlopen(url, timeout=self._online_timeout)
                content = response.read()
                break
            except urllib.error.HTTPError as err:  # 404
                raise OnlineError(str(err))
            except (socket.timeout, urllib.error.URLError) as err:  # timed out
                attempts += 1
                if self._online_max_attempts == attempts:
                    self.failed_list.append(team_id)
                    self.logger.error("[ERROR] %d: %s" % (team_id, err))
                    self.file_cnt += 1
                    raise OnlineError("Maximum Attempts Reached, %s" % str(err))
                continue

        self.logger.debug("\tStream Accessed at Attempt #%d" % attempts)
        return content

    def online_parser(self, team_id_lst):
        """
        Parse info from online (source) PDFs, and output as JSON
        :param team_id_lst: <list> of <int> team numbers
        """
        print("Running Online Parser ...\n")
        self.report_exec(online=True)
        time.sleep(0.5)

        conti_err_cnt = 0
        max_conti_err_reached = False
        for team_id in tqdm(team_id_lst):
            self.logger.info("Working on %d" % team_id)

            if max_conti_err_reached:
                self.logger.debug("\tClearing Queue (Max Conti-Error Cnt Reached)")
                continue
            if conti_err_cnt >= self._online_max_conti_err:
                max_conti_err_reached = True
                self.logger.critical(
                    "Maximum Continuous Error Count (%d) Reached. To End Crawler Workflow"
                    % self._online_max_conti_err)
                continue

            try:
                content = self.request_pdf_stream(team_id)
                self.file_cnt += 1
                conti_err_cnt = 0
            except Exception as err:
                self.logger.error("[ERROR] %s" % err)
                conti_err_cnt += 1
                continue

            try:
                info = self.translate_pdf(filename=None, filestream=content, fs_team_id=team_id)
                self.update_res_to_cache(info)
                self.suc_cnt += 1
            except Exception as err:
                self.failed_list.append(team_id)
                self.logger.error("[ERROR] %s" % err)
                continue

            self.logger.info("Parser Finished for %d" % team_id)

        self.cache_to_json()
        self.report_del()


class ParserErrors(Exception):
    def __init__(self):
        pass

    def __del__(self):
        pass


class LocalError(ParserErrors):
    def __init__(self, msg=""):
        self.msg = "[ERROR] LocalError: " + msg

    def __str__(self):
        return self.msg


class OnlineError(ParserErrors):
    def __init__(self, msg=""):
        self.msg = "[ERROR] OnlineError: " + msg

    def __str__(self):
        return self.msg


class ParsingError(ParserErrors):
    def __init__(self, msg=""):
        self.msg = "[ERROR] ParsingError: " + msg

    def __str__(self):
        return self.msg


class PDF2IMGError(ParserErrors):
    def __init__(self, msg=""):
        self.msg = "[ERROR] PDF2IMGError: " + msg

    def __str__(self):
        return self.msg


class IMGCropperError(ParserErrors):
    def __init__(self, msg=""):
        self.msg = "[ERROR] IMGCropperError: " + msg

    def __str__(self):
        return self.msg


if __name__ == "__main__":
    PATH = r"...\202004 MCM_ICM Results\MCM_ICM"

    kwargs = {"report_filename": "report_test", "result_filename": "result_test.json",
              "delete_cache": True, "cache_img_stream": True,
              "_online_max_conti_err": 1000, "_online_timeout": 5, "_online_max_attempts": 2}

    # # Local Parser
    # Logger = create_logger(os.path.join(PATH, "log"), less_log=True)
    # pt = PrizeParser(PATH, files_path="2020 MCM_ICM 获奖证书-20200428/",
    #                  logger=Logger, **kwargs)
    # file_list = pt.get_files_names()
    # pt.local_parser(file_list)

    # # Online Parser
    # Logger = create_logger(os.path.join(PATH, "log"), less_log=True)
    # pt = PrizeParser(PATH, logger=Logger, **kwargs)
    # pt.online_parser(range(2000000, 2099999))
    
    print("Welcome to MCM/ICM Parser. Please edit annotations to start executions.")