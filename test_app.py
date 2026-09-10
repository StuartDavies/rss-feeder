import unittest
from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET

from app import app


class FeedTests(unittest.TestCase):
    @patch("app.requests.post")
    def test_news_text_is_preserved_in_valid_xml(self, post):
        article = {
            "title": 'News & previews <today> "special"',
            "excerpt": '<p>Space Marines & heroes&nbsp; return.</p>',
            "uri": "/news/example/?a=1&b=2",
            "date": "10 Sep 26",
            "uuid": "example&123",
        }
        post.return_value = Mock(status_code=200)
        post.return_value.json.return_value = {"news": [article]}

        response = app.test_client().get("/warhammer-community")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/rss+xml")
        root = ET.fromstring(response.data)
        item = root.find("channel/item")
        self.assertEqual(item.findtext("title"), article["title"])
        self.assertEqual(item.findtext("description"), article["excerpt"])
        self.assertEqual(item.findtext("link"), "https://www.warhammer-community.com/en-gb" + article["uri"])
        self.assertEqual(item.findtext("guid"), article["uuid"])
        self.assertEqual(item.findtext("pubDate"), "Thu, 10 Sep 2026 00:00:00 GMT")
        self.assertEqual(item.find("guid").get("isPermaLink"), "false")
        self.assertIsNotNone(root.find("channel/{http://www.w3.org/2005/Atom}link"))


if __name__ == "__main__":
    unittest.main()
