
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
import requests
from bs4 import BeautifulSoup
import csv

app = FastAPI()
SCRAPED_FILE = "scraped_data.csv"
CATEGORY_URL = "https://www.argos.co.uk/browse/home-and-furniture/c:29351/"

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return '''
    <html>
        <head><title>ShopWise Argos Scraper</title></head>
        <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
            <h1>🛍️ ShopWise Argos Scraper</h1>
            <form action="/run" method="get">
                <button style="padding: 10px 20px; font-size: 16px;">▶️ Run Scraper</button>
            </form><br>
            <a href="/download"><button style="padding: 10px 20px; font-size: 16px;">📥 Download CSV</button></a>
        </body>
    </html>
    '''

@app.get("/run")
def run_scraper():
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(CATEGORY_URL, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    product_cards = soup.select("div[data-test='component-product-card']")
    products = []

    for card in product_cards[:20]:
        title_tag = card.select_one("img")
        price_tag = card.select_one("[data-test='product-card-price']")

        title = title_tag["alt"].strip() if title_tag and title_tag.has_attr("alt") else "N/A"
        price = price_tag.text.strip() if price_tag else "N/A"
        products.append([title, price])

    with open(SCRAPED_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Price"])
        writer.writerows(products)

    return HTMLResponse("<h2>✅ Scraping complete. <a href='/'>Go back</a></h2>")

@app.get("/download")
def download_csv():
    return FileResponse(SCRAPED_FILE, media_type="text/csv", filename=SCRAPED_FILE)
