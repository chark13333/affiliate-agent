"""ทดสอบ agent โดยตรงโดยไม่ต้องผ่าน LINE"""
import asyncio
from agent import process_message


async def main():
    test_queries = [
        "อยากได้หูฟัง bluetooth ราคาไม่เกิน 1500 บาท",
        "แนะนำโน้ตบุ๊คสำหรับทำงาน งบ 20000",
        "ครีมกันแดดที่ดีราคาไม่แพง",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"คำถาม: {query}")
        print(f"{'='*60}")
        response = await process_message(query)
        print(response)


if __name__ == "__main__":
    asyncio.run(main())
