import hashlib
import hmac
import time
import urllib.parse
import httpx
from config import SHOPEE_PARTNER_ID, SHOPEE_PARTNER_KEY, SHOPEE_AFFILIATE_ID

BASE_URL = "https://partner.shopeemobile.com/api/v2"


def _sign(path: str, timestamp: int, body: str = "") -> str:
    base = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{body}"
    return hmac.new(
        SHOPEE_PARTNER_KEY.encode(),
        base.encode(),
        hashlib.sha256
    ).hexdigest()


def _affiliate_url(product_url: str) -> str:
    if not SHOPEE_AFFILIATE_ID:
        return product_url
    encoded = urllib.parse.quote(product_url, safe="")
    return f"https://s.shopee.co.th/affiliate?aff_id={SHOPEE_AFFILIATE_ID}&url={encoded}"


async def search_products(keyword: str, limit: int = 3, max_price: float = None) -> list[dict]:
    timestamp = int(time.time())
    path = "/product/search_item"
    sign = _sign(path, timestamp)

    params = {
        "partner_id": SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "sign": sign,
        "keyword": keyword,
        "limit": min(limit, 10),
        "page_no": 0,
        "sort_type": 2,  # 2 = by sales
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BASE_URL}{path}", params=params)
        data = resp.json()

    products = []
    for item in data.get("response", {}).get("item", [])[:limit]:
        price_info = item.get("price_info", [{}])[0]
        # Shopee stores price in lowest denomination (x100000)
        price = float(price_info.get("current_price", 0)) / 100000
        if max_price and price > max_price:
            continue

        shop_id = item.get("shopid", "")
        item_id = item.get("itemid", "")
        product_url = f"https://shopee.co.th/product/{shop_id}/{item_id}"

        products.append({
            "platform": "Shopee",
            "name": item.get("name", ""),
            "price": price,
            "image": f"https://cf.shopee.co.th/file/{item.get('image', '')}",
            "rating": float(item.get("item_rating", {}).get("rating_star", 0)),
            "sold": item.get("sold", 0),
            "url": product_url,
            "affiliate_url": _affiliate_url(product_url),
        })

    return products
