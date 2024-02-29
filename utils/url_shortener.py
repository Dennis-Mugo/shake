import requests

class URLShortener:
    def __init__(self):
        pass

    def get_short_url(self, url):
        print("Shortening url...")
        self.url = url
        if "tinyurl" in self.url:
            return self.url
        response = requests.get(f"https://tinyurl.com/api-create.php?url={self.url}")
        
        return response.text

url_shortener = URLShortener()
