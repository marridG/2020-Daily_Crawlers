# Daily Crawlers
Written in Python 3.7.6  
Some Crawlers for Daily Data Collection  


## Table of Contents
<!-- MarkdownTOC  autolink="true" -->

- [Usage](#usage)
- [Declaration](#declaration)
- [202004 SJTU Zhiyuan College Namelist](#202004-sjtu-zhiyuan-college-namelist)
  - [Description](#description)
  - [Sample File Tree](#sample-file-tree)
  - [Getting Started](#getting-started)
  - [Results](#results)
- [202005 High School Rewards Crawler](#202005-high-school-rewards-crawler)
  - [Description](#description-1)
  - [Sample File Tree](#sample-file-tree-1)
  - [Getting Started](#getting-started-1)
  - [Results](#results-1)

<!-- /MarkdownTOC -->


## Usage
- Simply clone/download the files in the repository
- Ensure all "`import`"s (modules/packages) are installed
- Specify path, check global variables
- Run the codes and *have a cup of coffee* when you wait for the execution


## Declaration
All data belong to the corresponding source sites. The crawlers (sometimes together with crawled data) are provided only for proper private use. Anyone who risk abusing, in any forms, is to be blamed and should shoulder the responsibility on his/her own.  
Refer to the corresponding data source sites for more detailed privacy, distribution, etc. rules.

## 202004 SJTU Zhiyuan College Namelist
### Description
- **Functionality**: It crawls the information of the students involved in Shanghai Jiaotong University (SJTU) Zhiyuan College. Contents include:
    + Names lists of students of all majors and years
    + Students' self description
    + Students' profiles
- **Source**: [SJTU Zhiyuan College - Students](https://zhiyuan.sjtu.edu.cn/articles/625)

### Sample File Tree
```
  --- OUTPUT_DES_ROOT      <folder>    make sure path exists
   |--- OUTPUT_DES_FOLDER  <folder>    root of crawled results
     |--- &&&.xlsx         <file>      result file
     |--- &&&.jpg          <file>      profiles, filename format "major year id name.jpg"
```

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

### Results
Generally speaking, the results are stored in a `.xlsx` file. They are fairly comprehensive.


## 202005 High School Rewards Crawler  
### Description
- **Functionality**: It crawls results of several national adolescents science and technology competitions. Contents include:
    + Winners name lists of each competition
    + Sample certificates
    + Detailed information (links, source, subject, etc.) of the crawled data
- **Source**: [Children and Youth Science Center China Association for Science and Technology](http://gs.cyscc.org/)

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

### Getting Started
Please check the following necessary Python modules/packages  
```
  os, shutil, datetime, logging, json, tqdm, urllib, re, bs4
```

There are also some global variables that you may be concerned about, for an easier use:
- `URL_ROOT': Source URL. Please do NOT modify unless invalid.
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

### Results
Generally speaking, the results are stored in `.json` files. They are fairly comprehensive.
