import requests
from bs4 import BeautifulSoup


def expand_url(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.url
    except:
        return url


def extract_product_from_url(url):
    try:
        # 🔥 Expand short links
        url = expand_url(url)

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return {"error": "Failed to fetch page"}

        soup = BeautifulSoup(response.text, "html.parser")

        # -------------------------
        # Title Extraction (FIXED)
        # -------------------------
        title = ""

        # Amazon
        tag = soup.find(id="productTitle")
        if tag:
            title = tag.get_text(strip=True)

        # Flipkart
        elif soup.find("span", {"class": "B_NuCI"}):
            title = soup.find("span", {"class": "B_NuCI"}).get_text(strip=True)

        # Meta fallback (VERY IMPORTANT)
        elif soup.find("meta", property="og:title"):
            title = soup.find("meta", property="og:title")["content"]

        # Final fallback
        elif soup.title:
            title = soup.title.get_text(strip=True)

        # 🔥 Filter wrong titles
        if not title or "amazon" in title.lower():
            return {"error": "Could not extract actual product. Use full product link."}

        # -------------------------
        # Description Extraction (FIXED)
        # -------------------------
        desc_list = []

        bullets = soup.find_all("li")

        for b in bullets[:15]:
            text = b.get_text(strip=True)
            if len(text) > 30:
                desc_list.append(text)

        desc = " ".join(desc_list)

        return {
            "title": title,
            "description": desc
        }

    except Exception as e:
        return {"error": str(e)}