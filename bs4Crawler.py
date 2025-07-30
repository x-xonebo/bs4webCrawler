from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)

@app.route('/crawl-naver-news', methods=['POST'])
def crawl_naver_news_headlines_api():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error":"URL을 request body에 포함시키삼."}), 400

    target_url = data['url']

    if not target_url.startswith('http://') and not target_url.startswith('https://'):
        return jsonify({"error":"올바른 URL 형식이 아님요"}), 400

    if "news.naver.com" not in target_url:
        return jsonify({"error": "이 실습용 API는 네이버 뉴스만 크롤링 가넝~~"}), 400
    

    print(f"크롤링 요청 잘 들어옴ㅇㅇ: {target_url}")

    headlines = []
    try:

        response = requests.get(target_url, timeout=10)
        response.raise_for_status() #requests.exceptions.HTTPError

        soup = BeautifulSoup(response.text, 'html.parser')

        with open("crawled_naver_news.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        print("html 저장 완료")

        news_items = soup.find_all('a', class_='cnf_news_area')

        if news_items:

            for i, item in enumerate(news_items, start=1):

                title_tag = item.find('strong', class_='cnf_news_title')

                if title_tag:
                    title = title_tag.get_text(strip=True)
                    link = item.get('href') #get method 쓰면 속성 없을 때 None 반환 -> 오류 방지
                    #title_tag['href'] 이렇게 안하는 이유

                    headlines.append({"title": title, "link": link})
                else:
                    print(f" {i}번째 아이템에서 제목 태그 (strong, class='cnf_news_title')를 찾을 수 없음.")

        else:
            print(f"경고: {target_url}에 뉴스 헤드라인이 엄슴. 페이지 구조가 바꼈을 수도 있으니 구조 파악해서 소스 수정하삼")

        return jsonify({"status": "success", "url": target_url, "headlines": headlines})


    except requests.exceptions.Timeout:
        return jsonify({"error": "타임아웃 났음"})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"웹페이지 가져오다가 이런 오류 발생함 ->{e}"}),500
    except Exception as e:
        return jsonify({"error": f"크롤링 하다가 이런 오류 발생함 ->{e}"}),500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)