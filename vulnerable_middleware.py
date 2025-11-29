from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
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
async def vulnerable_middleware(request: Request, call_next):
    if request.url.path == "/":
        return await call_next(request)

    print("Starting request processing")

    response = await call_next(request)

    await simulate_settlement()
    settlement_success = False

    if settlement_success:
        print("Settlement succeeded")
        return response
    else:
        # @souhailaS: settlement failed, but response is already sent partially..
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
        print("Yielding chunk 1")
        yield b"chunk 1\n"
        await asyncio.sleep(0.1)
        print("Yielding chunk 2")
        yield b"chunk 2\n"
        await asyncio.sleep(0.1)
        print("Yielding final chunk")
        yield b"final chunk\n"

    return StreamingResponse(generate(), media_type="text/plain")


if __name__ == "__main__":
    print("Watch server logs .. content is sent BEFORE settlement completes")
    uvicorn.run(app, host="0.0.0.0", port=8000)


