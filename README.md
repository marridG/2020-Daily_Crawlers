# Daily Crawlers
Written in Python 3.7.6  
Some Crawlers for Daily Data Collection  

<!-- MarkdownTOC -->

- Install
- Declaration
- Crawlers Description
  - 202005 High School Rewards Crawler
    - Description
    - Sample File Tree
    - Get Started
    - Results

<!-- /MarkdownTOC -->



## Install
- Simply clone/download the files in the repository
- Ensure all "`import`"s are installed
- Check Path
- Run codes

## Declaration
All data belong to the corresponding source sites. The crawlers (sometimes together with crawled data) are provided only for proper private use. Anyone who risk abusing, in any forms, is to be blamed and should shoulder the responsibility on his/her own.  
Refer to the corresponding data source sites for more detailed privacy, distribution, etc. rules.


## Crawlers Description
### 202005 High School Rewards Crawler  
#### Description
- **Functionality**: It crawls results of several national adolescents science and technology competitions. Contents include:
    + Winners name lists of each competition
    + Sample certificates
    + Detailed information (links, source, subject, etc.) of the crawled data
- **Source**: [Children and Youth Science Center China Association for Science and Technology](http://gs.cyscc.org/)

#### Sample File Tree
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

#### Get Started
Please check the following necessary Python modules/packages  
`os, shutil, datetime, logging, json, tqdm, urllib, re, bs4`

There are also some global variables that you may be concerned about, for an easier use:
- `FILE_ROOT`: Project-based workspace, also the path where all results and caches are stored. Please make sure such a path exists. All file operations are done in such a path.
- `FILE_DES_ROOT`: Path (relative) where the results of a crawl are stored, default labeled with a timestamp.
- `FILE_DECL_NAME`: File name of the file where the declarations on the source site is stored.
- `FILE_DES_CERT`: Path (relative) where the files related to the sample certificates are stored.
- `FILE_RES_NAME`: File name of the file where the name lists results are stored.
- `FILE_LOG_NAME`: File name of the file where logs are stored.
- `FILE_NL_SRC_NAME`: File name of the file where the links and info of name lists are stored.
- `FILE_CACHE_PATH`: Path (relative) of the cache folder
- `TARGET_SAMPLE_CERT`: Mode selection, whether to crawl the sample certificates
- `LESS_CONSOLE_LOG`: Mode selection, whether to show less debug logs in console

#### Results
Generally speaking, the results are stored in a form of .json files. They are fairly comprehensive.
