import hashlib
import hmac
import time
import urllib.parse
import httpx
from config import LAZADA_APP_KEY, LAZADA_APP_SECRET, LAZADA_TRACKING_ID

BASE_URL = "https://api.lazada.co.th/rest"


def _sign(params: dict, path: str) -> str:
    sorted_params = sorted(params.items())
    params_str = path + "".join(f"{k}{v}" for k, v in sorted_params)
    return hmac.new(
        LAZADA_APP_SECRET.encode(),
        params_str.encode(),
        hashlib.sha256
    ).hexdigest().upper()


def _affiliate_url(product_url: str) -> str:
    if not LAZADA_TRACKING_ID:
        return product_url
    encoded = urllib.parse.quote(product_url, safe="")
    return f"https://c.lazada.co.th/t/c.{LAZADA_TRACKING_ID}?url={encoded}"


async def search_products(keyword: str, limit: int = 3, max_price: float = None) -> list[dict]:
    timestamp = str(int(time.time() * 1000))
    params = {
        "app_key": LAZADA_APP_KEY,
        "timestamp": timestamp,
        "sign_method": "sha256",
        "keyword": keyword,
        "page_size": str(min(limit, 10)),
        "page_no": "1",
        "sort_by": "pop",  # sort by popularity
    }
    if max_price:
        params["price_max"] = str(int(max_price * 100))

    path = "/products/search"
    params["sign"] = _sign(params, path)

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BASE_URL}{path}", params=params)
        data = resp.json()

    products = []
    for item in data.get("data", {}).get("products", [])[:limit]:
        sku = item.get("skus", [{}])[0]
        price = float(sku.get("special_price") or sku.get("price", 0))
        product_url = item.get("url", "")
        products.append({
            "platform": "Lazada",
            "name": item.get("name", ""),
            "price": price,
            "image": item.get("primary_category", {}).get("image", "") or sku.get("Images", [""])[0],
            "rating": float(item.get("item_rating", {}).get("rating_star", 0)),
            "sold": item.get("sold", 0),
            "url": product_url,
            "affiliate_url": _affiliate_url(product_url),
        })

    return products
