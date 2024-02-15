import requests
from bs4 import BeautifulSoup
import logging
import sys
sys.path.append('../')

from data.News import News
import utils.Config

def extractHeadlineUrl(sid : int, page : int) -> list :
    ### 뉴스 분야(sid)와 페이지(page)를 입력하면 그에 대한 링크들을 리스트로 추출하는 함수 ###
    ## 1. headline 기사만 추출된다.
    url = f"https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1={sid}#&date=%2000:00:00&page={page}"
    try :
        html = requests.get(url, headers={"User-Agent": utils.Config.getConfigData("request_header").get("User-Agent")})
        if html.status_code != 200 :
            raise Exception("headline crawl failed")
    except Exception as e :
        logging.getLogger('__main__').error(e)
        return []
    soup = BeautifulSoup(html.text, "lxml")
    headline_tag = soup.find_all('a', attrs={"class": "sa_text_title", "data-clk" : "airscont"})
    ## 2.
    url_set = set()
    for ex in headline_tag:
        if ("href" in ex.attrs) :
            url_set.add(ex["href"])
    return list(url_set)

def extractNewsFromUrl(url : str) -> News :
    try :
        html = requests.get(url, headers={"User-Agent": utils.Config.getConfigData("request_header").get("User-Agent")})
        if html.status_code != 200 :
            raise Exception("news data crawl failed")
    except Exception as e :
        logging.getLogger('__main__').error(e)
        return None
    soup = BeautifulSoup(html.text, "lxml")
    news = News()
    # 제목
    meta = soup.find('meta', attrs = {"property" : "og:title"})
    news.title = meta.get("content").replace('\"', '\\"').replace('\'', "\\'")
    # 사진 링크
    meta = soup.find('meta', attrs = {"property" : "og:image"})
    news.imgLink = meta.get("content")
    # 요약
    meta = soup.find('meta', attrs = {"property" : "og:description"})
    news.description = meta.get("content").replace('\"', '\\"').replace('\'', "\\'") + "..."
    # 강조 구문
    try :
        news.description = meta.find('strong').get_text() + "..."
    except Exception as e :
        pass
    # 본문 링크
    meta = soup.find('meta', attrs = {"property" : "og:url"})
    news.naverLink = meta.get("content")
    # 발행일
    meta = soup.find('span', attrs = {"class" : "media_end_head_info_datestamp_time _ARTICLE_DATE_TIME"})
    try :
        news.pubDate = meta.get("data-date-time").replace(' ', 'T')
    except Exception as e :
        return None
    return news