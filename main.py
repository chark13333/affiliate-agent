import asyncio
import hashlib
import hmac
import json

import httpx
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    PushMessageRequest,
    ShowLoadingAnimationRequest,
    TextMessage,
)
from linebot.v3 import WebhookParser
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from agent import process_message
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET

app = FastAPI(title="Affiliate Agent Bot")
_line_config = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
_parser = WebhookParser(LINE_CHANNEL_SECRET)


async def _push(user_id: str, text: str) -> None:
    async with AsyncApiClient(_line_config) as api_client:
        api = AsyncMessagingApi(api_client)
        await api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=text)],
            )
        )


async def _handle_event(event: MessageEvent) -> None:
    if not isinstance(event.message, TextMessageContent):
        return

    user_id = event.source.user_id
    text = event.message.text

    try:
        async with AsyncApiClient(_line_config) as api_client:
            api = AsyncMessagingApi(api_client)
            await api.show_loading_animation(
                ShowLoadingAnimationRequest(chat_id=user_id)
            )
    except Exception:
        pass

    try:
        reply_text = await process_message(text)
        await _push(user_id, reply_text)
    except Exception as e:
        import traceback, logging
        logging.error(f"ERROR: {e}\n{traceback.format_exc()}")
        try:
            await _push(user_id, f"ขออภัย เกิดข้อผิดพลาด กรุณาลองใหม่ครับ")
        except Exception:
            pass


@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()

    try:
        events = _parser.parse(body.decode(), signature)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if isinstance(event, MessageEvent):
            background_tasks.add_task(_handle_event, event)

    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
