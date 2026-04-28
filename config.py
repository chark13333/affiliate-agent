import os
from dotenv import load_dotenv

load_dotenv()

# LINE Bot
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")

# Claude
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Lazada Open Platform (https://open.lazada.com)
LAZADA_APP_KEY = os.getenv("LAZADA_APP_KEY", "")
LAZADA_APP_SECRET = os.getenv("LAZADA_APP_SECRET", "")
LAZADA_TRACKING_ID = os.getenv("LAZADA_TRACKING_ID", "")  # affiliate tracking code

# Shopee Open Platform (https://open.shopee.com)
SHOPEE_PARTNER_ID = os.getenv("SHOPEE_PARTNER_ID", "")
SHOPEE_PARTNER_KEY = os.getenv("SHOPEE_PARTNER_KEY", "")
SHOPEE_AFFILIATE_ID = os.getenv("SHOPEE_AFFILIATE_ID", "")
