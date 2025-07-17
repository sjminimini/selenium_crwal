import urllib.robotparser
from urllib.parse import urlparse, quote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import time

def is_allowed_by_robots(url, user_agent='*'):
    """
    robots.txt 파일을 확인하여 해당 URL 크롤링이 허용되는지 검사하는 함수.
    user_agent 기본값은 '*' (모든 사용자 에이전트)
    """
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    robots_url = f"{base_url}/robots.txt"

    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read() # robots.txt 읽기 시도
        return rp.can_fetch(user_agent, url) # 크롤링 허용 여부 반환 (True/False)
    except Exception as e:
        print(f"[ERROR] robots.txt 읽기 실패: {e}")
        return False  # 실패 시 안전하게 금지

def crawl_and_screenshot(url):
    """
    Selenium을 이용해 헤드리스 크롬 브라우저로 웹페이지를 열고,
    전체 페이지 높이에 맞춰 창 크기를 조절한 뒤 스크린샷을 저장하는 함수
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = ChromeService()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url) # URL 접속
        time.sleep(3)  # 페이지 로딩 대기

        # 페이지 전체 높이로 브라우저 창 크기 조정
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        # 창 크기를 전체 페이지 높이에 맞게 설정
        driver.set_window_size(1920, scroll_height)
        time.sleep(1)  # 창 크기 반영 대기

        # URL을 기반으로 파일명 생성
        parsed = urlparse(url)
        domain_part = parsed.netloc.replace('.', '_')
        path_part = quote(parsed.path.strip('/').replace('/', '_'))

        screenshot_path = domain_part
        if path_part:
            screenshot_path += "_" + path_part
        screenshot_path += ".png"

        driver.save_screenshot(screenshot_path) # 스크린샷 저장
        print(f"[스크린샷 저장] {screenshot_path}")
    except Exception as e:
        print(f"[ERROR] Selenium 크롤링 실패: {e}")
    finally:
        driver.quit() # 브라우저 종료

# 크롤링 대상 URL 리스트
urls_to_crawl = [
    "크롤링할 url"
]

for url in urls_to_crawl: # robots.txt 검사 후 허용된 경우에만 크롤링 실행
    if is_allowed_by_robots(url):
        print(f"[허용] 크롤링 진행: {url}")
        crawl_and_screenshot(url)
    else:
        print(f"[금지] robots.txt 규칙에 따라 크롤링 금지: {url}")
