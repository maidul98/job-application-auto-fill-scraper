#!flask/bin/python
from flask import Flask
from flask import jsonify
from flask import request
from flask import abort
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/scrape-linkedin', methods=['GET'])
def scrapeLinkedIn():
    if not request.json or not "url" in request.json:
        abort(300)

    url  = request.json['url']
    if "jobs/view/" in url:
        return scraper(url)

    elif 'position' in url:
        hashMap = {}
        for item in url.split('&'):
            if "position" in item:
                job_num = int(item.split('=')[1])
                pageData = requests.get(url)
                soup = BeautifulSoup(pageData.text, 'html.parser')
                singlePageURL = \
                soup.find(class_='jobs-search__results-list').find_all('li')[job_num - 1].find('a').attrs['href']
                return scraper(singlePageURL)
    else:
        return jsonify({}), 400


def scraper(url):
    hashMap = {}
    singlePageJobLisitng = requests.get(url)
    soup = BeautifulSoup(singlePageJobLisitng.text, 'html.parser')
    hashMap['job-title'] = soup.find(class_="topcard__title").text
    hashMap['job-location'] = soup.find(class_="topcard__flavor topcard__flavor--bullet").text
    hashMap['company-name'] = soup.find(class_="topcard__org-name-link topcard__flavor--black-link").text.capitalize()
    hashMap['company-icon'] = ''
    hashMap['job-posting'] = soup.find(class_='description__text description__text--rich').decode_contents()
    return jsonify(hashMap), 201

if __name__ == '__main__':
    app.run(debug=True)