# Daily Crawlers
Written in `Python 3.7.6`  

Some Crawlers for Daily Data Collection  

<br>

## Table of Contents
<!-- MarkdownTOC  autolink="true" -->

- [Usage](#usage)
- [Declaration](#declaration)
- [SJTU Zhiyuan College Namelist](#sjtu-zhiyuan-college-namelist)
    - [Description](#description)
    - [Sample File Tree](#sample-file-tree)
    - [Getting Started](#getting-started)
    - [Results](#results)
- [MCM/ICM Results](#mcmicm-results)
    - [Description](#description-1)
    - [Sample File Tree](#sample-file-tree-1)
    - [Getting Started](#getting-started-1)
    - [Results](#results-1)
- [High School Rewards Crawler](#high-school-rewards-crawler)
    - [Description](#description-2)
    - [Sample File Tree](#sample-file-tree-2)
    - [Getting Started](#getting-started-2)
    - [Results](#results-2)

<!-- /MarkdownTOC -->


<br>


<a id="usage"></a>
## Usage
1. Simply clone/download the files in the repository
2. Ensure all \"`import`\"s (modules/packages) are installed
3. Specify path, check global variables
4. Run the codes and *have a cup of coffee* when you wait for the execution


<a id="declaration"></a>
## Declaration
All data belong to the corresponding source sites. The crawlers (sometimes together with crawled data) are provided only for proper private use. Anyone who risk abusing, in any forms, is to be blamed and should shoulder the responsibility on his/her own.  

**IMPORTANT REMINDER**  
1. Please refer to the corresponding data source sites for more detailed rules (with regard to privacy, distribution, etc.).  
2. Please wisely use data.


<br><br>





<a id="sjtu-zhiyuan-college-namelist"></a>
## SJTU Zhiyuan College Namelist
<a id="description"></a>
### Description
- **Repository Folder Name**: `./202004 SJTU Zhiyuan Namelist/`  
- **Functionality**: It crawls the information of the students involved in Shanghai Jiaotong University (SJTU) Zhiyuan College.  
    Contents include:
    + Names lists of students of all majors and years
    + Students' self description
    + Students' profiles
- **Source**: [SJTU Zhiyuan College - Students](https://zhiyuan.sjtu.edu.cn/articles/625)

<a id="sample-file-tree"></a>
### Sample File Tree
```
  --- OUTPUT_DES_ROOT      <folder>    make sure path exists
   |--- OUTPUT_DES_FOLDER  <folder>    root of crawled results
     |--- &&&.xlsx         <file>      result file
     |--- &&&.jpg          <file>      profiles, filename format "major year id name.jpg"
```

<a id="getting-started"></a>
### Getting Started
Please check the following necessary Python modules/packages  
```
  os, shutil, datetime, time, logging, json, tqdm, urllib, re, bs4, string, lxml, html2text, numpy, pandas
```

There are also some global variables that you may be concerned about, for an easier use:  
- `ROOT`: Root URL of source site. Please do not modify unless invalid.
- `NAME_LIST_URL`: URL of source page. Please do not modify unless invalid.  
- `OUTPUT_DES_ROOT`: Project-based workspace. Please make sure such a path exists. All file operations are done in such a path.  
- `TIME_STAMP`: Timestamp, used in path naming.  
- `OUTPUT_DES_FOLDER`: Path (relative) where the results of a crawl are stored, default labeled with timestamp. All results files operations are done in such a path.  
- `SAVE_PAGE`: Mode selection, whether to save the web pages.  
- `SLEEP_INTERVAL`: Sleep intervals for executions to halt. For system use only, modifications NOT recommended.  
- `DEBUG_MODE`: Mode selection, whether to show less debug logs.  

<a id="results"></a>
### Results
Generally speaking, the results are stored in a `.xlsx` file. They are fairly comprehensive.



<br><br>













<a id="mcmicm-results"></a>
## MCM/ICM Results
<a id="description-1"></a>
### Description
- **Repository Folder Name**:  `./202004 MCM_ICM Results/`
- **Competitions**: [Mathematical Contest in Modeling, The Interdisciplinary Contest in Modeling](https://www.comap.com/undergraduate/contests/) (MCM/ICM for short)  
- **Functionality**: It crawls the competition results (Year 2019, 2020 tested) of MCM/ICM. Contents include:
    + The Crawler (in `Crawler.py`)
        * Certificate PDFs
    + The Parser (in `Parser.py`)
        * Winners teams list
        * Participants on each team
        * Advisor of each team
        * Prize Types
- **Source**: [COMAP - Problems and Results](https://www.comap.com/undergraduate/contests/mcm/previous-contests.php)
- **Special Notifications**
    + <u>Storage Concerns</u> about the Crawler: Please keep in mind that if you want to download all the certificates, an estimation of device storage should be made. For instance, 20951 certificates of Year 2020 takes up 3.18 GB (160 KB each file on average).
    + <u> Execution Resources Concerns</u> about the Crawler and the Parser: A large amount of resources (time, computational resources, Internet service, etc.) will be consumed during the process. It is much more critical for the Parser. Here are some of my execution time numbers (hour:minute:second):  
        * Year 2020, Crawler: 20:52:01 (20951 files)
        * Year 2020, Parser - Online Approach: 71:13:33 (20960 items)
        * Year 2019, Parser - Online Approach: 81:40:47 (25365 items)  
- **Possible Future Improvemnts**
    + <u>Efficiency</u>: Although great efforts have been taken to imporve the performance, to ensure the accuracy, network connection problems and the usage of some modules still result in a low efficiency. 
    + <u>PDF miner</u>: `fitz` is used here to convert PDF files containing rederable text areas to image data and then conduct further steps. If it is possible to parse text directly, great amount of time will be saved.
    + <u>Accuracy</u>: Frankly speaking, some of the particpants\' names are given in languages like Chinese instead of English. Although `pytesseract` supportss such languages, its accuracy is still a problem. As a result, non-English characters will possibly not be parsed well enough.
    + <u>During-Execution Cache Designs</u>: Currently, either memory cache or file I/O burdens the device a lot.  


<a id="sample-file-tree-1"></a>
### Sample File Tree
```
  --- FILE_ROOT             <folder>    make sure path exists
   |--- FILE_CACHE_PATH     <folder>    to be deleted when successfully terminated
   |--- FILE_DES_ROOT       <folder>    root of crawled results
     |--- FILE_DES_CERT     <folder>    stores the sample certificates
     |--- FILE_DECL_NAME    <file>      declarations from the source
     |--- FILE_RES_NAME     <file>      result file, in json format
     |--- FILE_LOG_NAME     <file>      log file
     |--- FILE_NL_SRC_NAME  <file>      "cache" like, contains all the sources of name lists
```

<a id="getting-started-1"></a>
### Getting Started
Please check the following necessary Python modules/packages  
```
  os, shutil, datetime, logging, json, tqdm, urllib, re, bs4
```

There are also some global variables that you may be concerned about, for an easier use:  
- `URL_ROOT`: Source URL. Please do NOT modify unless invalid.  
- `FILE_ROOT`: Project-based workspace, also the path where all results and caches are stored. Please make sure such a path exists. All file operations are done in such a path.  
- `FILE_DES_ROOT`: Path (relative) where the results of a crawl are stored, default labeled with a timestamp.  
- `FILE_DECL_NAME`: File name of the file where the declarations on the source site is stored.  
- `FILE_DES_CERT`: Path (relative) where the files related to the sample certificates are stored.  
- `FILE_RES_NAME`: File name of the file where the name lists results are stored.  
- `FILE_LOG_NAME`: File name of the file where logs are stored.  
- `FILE_NL_SRC_NAME`: File name of the file where the links and info of name lists are stored.  
- `FILE_CACHE_PATH`: Path (relative) of the cache folder. Modifications NOT recommended.  
- `TARGET_SAMPLE_CERT`: Mode selection, whether to crawl the sample certificates.  
- `LESS_CONSOLE_LOG`: Mode selection, whether to show less debug logs in console.  

<a id="results-1"></a>
### Results
Generally speaking, the results are stored in `.json` files. They are fairly comprehensive.



<br><br>









<a id="high-school-rewards-crawler"></a>
## High School Rewards Crawler  
<a id="description-2"></a>
### Description
- **Repository Folder Name**:  `./202005 High School Rewards Crawler/`
- **Functionality**: It crawls results of several national adolescents science and technology competitions.  
    Contents include:
    + Winners name lists of each competition
    + Sample certificates
    + Detailed information (links, source, subject, etc.) of the crawled data
- **Source**: [Children and Youth Science Center China Association for Science and Technology](http://gs.cyscc.org/)

<a id="sample-file-tree-2"></a>
### Sample File Tree
```
  --- FILE_ROOT             <folder>    make sure path exists
   |--- FILE_CACHE_PATH     <folder>    to be deleted when successfully terminated
   |--- FILE_DES_ROOT       <folder>    root of crawled results
     |--- FILE_DES_CERT     <folder>    stores the sample certificates
     |--- FILE_DECL_NAME    <file>      declarations from the source
     |--- FILE_RES_NAME     <file>      result file, in json format
     |--- FILE_LOG_NAME     <file>      log file
     |--- FILE_NL_SRC_NAME  <file>      "cache" like, contains all the sources of name lists
```

<a id="getting-started-2"></a>
### Getting Started
Please check the following necessary Python modules/packages  
```
  os, shutil, datetime, logging, json, tqdm, urllib, re, bs4
```

There are also some global variables that you may be concerned about, for an easier use:   
- `URL_ROOT`: Source URL. Please do NOT modify unless invalid.   
- `FILE_ROOT`: Project-based workspace, also the path where all results and caches are stored. Please make sure such a path exists. All file operations are done in such a path.  
- `FILE_DES_ROOT`: Path (relative) where the results of a crawl are stored, default labeled with a timestamp.  
- `FILE_DECL_NAME`: File name of the file where the declarations on the source site is stored.  
- `FILE_DES_CERT`: Path (relative) where the files related to the sample certificates are stored.  
- `FILE_RES_NAME`: File name of the file where the name lists results are stored.  
- `FILE_LOG_NAME`: File name of the file where logs are stored.  
- `FILE_NL_SRC_NAME`: File name of the file where the links and info of name lists are stored.  
- `FILE_CACHE_PATH`: Path (relative) of the cache folder. Modifications NOT recommended.  
- `TARGET_SAMPLE_CERT`: Mode selection, whether to crawl the sample certificates.  
- `LESS_CONSOLE_LOG`: Mode selection, whether to show less debug logs in console.  

<a id="results-2"></a>
### Results
Generally speaking, the results are stored in `.json` files. They are fairly comprehensive.
