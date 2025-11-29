from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse, Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import asyncio
import uvicorn
import os


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def secure_middleware(request: Request, call_next):
    if request.url.path == "/":
        return await call_next(request)

    print("Starting request processing")

    response = await call_next(request)



    response_body = b"" # @souhailaS: buffer the entire response because we may need to discard it
    async for chunk in response.body_iterator:
        response_body += chunk

    print(f"Buffered {len(response_body)} bytes")
    print("Content is NOT sent to client yet")

    print("Now performing settlement")
    await simulate_settlement()
    settlement_success = False

    if settlement_success:
        print("Settlement succeeded - delivering content")
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
    else:
        print("Settlement FAILED - returning 402, NO content leaked")
        return JSONResponse(
            status_code=402,
            content={"error": "Payment Required"}
        )


async def simulate_settlement():
    print("Settlement in progress...")
    await asyncio.sleep(0.5)
    print("Settlement complete")


@app.get("/")
async def serve_html():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    return FileResponse(html_path)


@app.get("/weather")
async def get_weather() -> Dict[str, Any]:
    return {
        "report": {
            "weather": "sunny",
            "temperature": 70,
        }
    }


@app.get("/stream")
async def paid():
    async def generate():
        print("Generating chunk 1")
        yield b"chunk 1\n"
        await asyncio.sleep(0.1)
        print("Generating chunk 2")
        yield b"chunk 2\n"
        await asyncio.sleep(0.1)
        print("Generating final chunk")
        yield b"final chunk\n"

    return StreamingResponse(generate(), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
