import json
import anthropic
from platforms.lazada import search_products as lazada_search
from platforms.shopee import search_products as shopee_search
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

TOOLS = [
    {
        "name": "search_lazada",
        "description": "ค้นหาสินค้าใน Lazada Thailand พร้อม affiliate link",
        "input_schema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "คำค้นหา เช่น 'หูฟัง bluetooth'"},
                "limit": {"type": "integer", "description": "จำนวนสินค้า 1-5 ชิ้น", "default": 3},
                "max_price": {"type": "number", "description": "ราคาสูงสุด (บาท)"},
            },
            "required": ["keyword"],
        },
    },
    {
        "name": "search_shopee",
        "description": "ค้นหาสินค้าใน Shopee Thailand พร้อม affiliate link",
        "input_schema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "คำค้นหา เช่น 'หูฟัง bluetooth'"},
                "limit": {"type": "integer", "description": "จำนวนสินค้า 1-5 ชิ้น", "default": 3},
                "max_price": {"type": "number", "description": "ราคาสูงสุด (บาท)"},
            },
            "required": ["keyword"],
        },
    },
]

SYSTEM_PROMPT = """คุณคือผู้ช่วยแนะนำสินค้าออนไลน์สำหรับคนไทย ชื่อว่า "ช้อปดี Bot"

หน้าที่:
- เมื่อผู้ใช้ถามหาสินค้า ให้ค้นหาทั้งใน Lazada และ Shopee พร้อมกัน
- แนะนำสินค้าที่ดีที่สุด 2-3 ชิ้นจากแต่ละแพลตฟอร์ม
- เปรียบเทียบราคาและบอกว่าซื้อที่ไหนคุ้มกว่า
- ใส่ affiliate_url เสมอ

กฎสำคัญ - ตอบเป็น PLAIN TEXT เท่านั้น ห้ามใช้ Markdown:
- ห้ามใช้ ** ## [] () ทุกชนิด
- ลิงก์ให้วางเป็น URL ตรงๆ เช่น https://...
- ใช้เครื่องหมาย --- คั่นแทน

รูปแบบการตอบ:
🛒 ชื่อสินค้า
💰 ราคา: ฿ราคา
⭐ เรท: x/5
🔗 https://affiliate_url_ตรงๆ

ตอบภาษาไทย กระชับ ไม่เกิน 5 รายการต่อแพลตฟอร์ม"""


async def process_message(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "ขออภัย ไม่พบสินค้าที่ต้องการ"

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = await _run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return "ขออภัย เกิดข้อผิดพลาด กรุณาลองใหม่"


async def _run_tool(name: str, inputs: dict) -> list:
    try:
        if name == "search_lazada":
            return await lazada_search(**inputs)
        elif name == "search_shopee":
            return await shopee_search(**inputs)
    except Exception as e:
        return [{"error": f"ค้นหาไม่สำเร็จ: {str(e)}"}]
    return []
