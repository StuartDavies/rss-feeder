from datetime import datetime
import uuid
from flask import Flask, json, jsonify, Response
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route('/warhammer-community')
def warhammer_community_feed():
    rss_content = """<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
        <channel>
            <title>Warhammer Community News Feed</title>
            <description>RSS feed generated from the Warhammer Community website</description>
            <link>https://www.warhammer-community.com/en-gb/all-news-and-features/</link>
            <atom:link href="https://www.redditchtabletopgamers.com/rss/warhammer-community" rel="self" type="application/rss+xml"/>
    """
    api_url = "https://www.warhammer-community.com/api/search/news/"
  
    payload = {
        "sortBy":"date_desc",
        "category":"",
        "collections":["articles"],
        "game_systems":[],
        "index":"news",
        "locale":"en-gb",
        "page":0,
        "perPage":16,
        "topics":[]
    }

    # Make the POST request to the external API
    response = requests.post(api_url, json=payload)

    # Return the response from the external API to the client
    if response.status_code == 200:
        content = response.json()

        for news_item in content["news"]:
            title = news_item["title"]
            description = news_item["excerpt"]
            link = news_item["uri"]
            date = news_item["date"]
            guid = news_item["uuid"]

            date_obj = datetime.strptime(date, "%d %b %y")
            rfc_822_date = date_obj.strftime("%a, %d %b %Y %H:%M:%S %z")

            rss_content += "<item>"
            rss_content += f"<title>{title}</title>"
            rss_content += f"<description>{description}</description>"
            rss_content += f"<link>https://www.warhammer-community.com/en-gb{link}</link>"
            rss_content += f"<pubDate>{rfc_822_date.rstrip()} GMT</pubDate>"
            rss_content += f"<guid isPermaLink=\"false\">{guid}</guid>"
            rss_content += "</item>"

        rss_content += """
            </channel>
        </rss>
        """

        xml = ET.XML(rss_content)
        ET.register_namespace("atom", "http://www.w3.org/2005/Atom")
        ET.indent(xml)
        xml = ET.tostring(xml, xml_declaration=True, encoding='utf-8', method="xml")
        
        return Response(xml, mimetype='application/rss+xml')

    else:
        return jsonify({
            "status": "failed",
            "error": response.text  # Return the error message
        }), response.status_code

@app.route('/test')
def test_feed():

    file = open("/data/test.rss", "r")
    xml = file.read()
    file.close()
    return Response(xml, mimetype='application/rss+xml')
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)