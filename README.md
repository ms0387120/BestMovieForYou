# Best Movie for You!

## Usage
- First, go to the `mysite` folder, and create a `config.yaml` file. For linux system:
```linux
cd mysite
cp config_template.yaml config.yaml
```
Inside the `config.yaml` file, fill in your OMDB api key.  
- Second, type the following command to launch the server:
```python
python manage.py runserver <port>
```
This will launch a local host on `<port>`.  
- Third, browse the website:
```
http://localhost:<port>
```
And, enjoy!

## Required packages:
```
beautifulsoup4==4.6.0
Django==1.11.2
httplib2==0.10.3
lxml==3.7.3
nltk==3.2.4
numpy==1.12.1
PyYAML==3.12
requests==2.11.1
scikit-learn==0.18.1
scipy==0.19.0
sklearn==0.0
```

## Data collected:
- Data sources: **OMDB**, **IMDB**
- Number of synopses:  
  `upcoming movies`: 23  
  `popular movies`: 7165  
  `now_playing movies`: 51  
  `top_rated movies`: 4321 
  
## Usage of Apriori in Jupyter:
-Read csv file
```
f = open('actor.csv','r')
```
-Run Apriori
 ```
!python apriori.py -f actor.csv -s [support num] -c [confidence num]
```

## Introduction
此電影推薦系統收集 2011 到 2016 年電影的相關資訊及評論，讓你能快速找到與輸入關鍵 字相似的電影，享受電影時光。在搜尋欄上輸入某部英文片名，然後從「現正熱映、即將上 映、popular、top rated」四選一，就會推薦出與輸入內容相似的電影。此項專案是跟著碩博班的研究生共同開發，**個人負責的功能為鐵三角組合及活躍演員名單**

* 程式語言: Python 
* 網站建置: Django、Bootstrap、jQuery 
* 資料來源: TMDB、IMDB 
* 功能: 推薦相似電影、鐵三角組合(演員之間的密切關係)、活躍演員名單(演出作品數量多寡)
* 套件使用: Requests(爬蟲)、BeautifulSoup(爬蟲)、NLTK(自然語言處理)、Scikit-Learn、Scipy(字袋向量化處理及運算)

![](https://i.imgur.com/NqDS65L.png)
![](https://i.imgur.com/RZFIw6B.png)
![](https://i.imgur.com/EM7McfL.png)
