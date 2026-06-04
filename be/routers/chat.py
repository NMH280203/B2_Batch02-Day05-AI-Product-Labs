import json
import sys
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from models.schemas import ChatRequest
from agents import orchestrator

router = APIRouter()


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    SSE endpoint cho chat.
    Từng event được stream theo format: event: {name}\\ndata: {json}\\n\\n
    """
    async def event_generator():
        async def stream_callback(event: str, data: dict):
            payload = json.dumps(data, ensure_ascii=False)
            yield f"event: {event}\ndata: {payload}\n\n"

        # Chạy generator thực
        async def run():
            chunks = []

            async def callback(event: str, data: dict):
                payload = json.dumps(data, ensure_ascii=False)
                chunks.append(f"event: {event}\ndata: {payload}\n\n")

            try:
                await orchestrator.run(
                    messages=request.messages,
                    context=request.context,
                    stream_callback=callback,
                )
            except Exception as e:
                print(f"[ERROR] Orchestrator failed: {e}", file=sys.stderr)
                error_payload = json.dumps({"message": str(e)}, ensure_ascii=False)
                chunks.append(f"event: error\ndata: {error_payload}\n\n")

            return chunks

        # Dùng async generator pattern đúng với FastAPI
        import asyncio

        queue: asyncio.Queue = asyncio.Queue()

        async def callback(event: str, data: dict):
            payload = json.dumps(data, ensure_ascii=False)
            await queue.put(f"event: {event}\ndata: {payload}\n\n")

        async def producer():
            try:
                await orchestrator.run(
                    messages=request.messages,
                    context=request.context,
                    stream_callback=callback,
                )
            except Exception as e:
                print(f"[ERROR] Orchestrator failed: {e}", file=sys.stderr)
                error_payload = json.dumps({"message": str(e)}, ensure_ascii=False)
                await queue.put(f"event: error\ndata: {error_payload}\n\n")
            finally:
                await queue.put(None)  # Sentinel

        producer_task = asyncio.create_task(producer())

        while True:
            item = await queue.get()
            if item is None:
                break
            yield item

        await producer_task

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
