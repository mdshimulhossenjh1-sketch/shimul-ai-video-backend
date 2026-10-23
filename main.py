import os
import asyncio
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from gradio_client import Client, handle_file

app = FastAPI(title="Shimul AI Video Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_SPACE = "Lightricks/LTX-Video"

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "Shimul AI Video Studio"
    }

@app.post("/generate")
async def generate_video(
    prompt: str = Form(...),
    duration: int = Form(3),
    image: UploadFile = File(None),
):
    if not prompt.strip():
        raise HTTPException(400, "Please enter a prompt.")

    if duration < 1 or duration > 5:
        raise HTTPException(400, "Duration must be between 1 and 5 seconds.")

    # Public demo connection; actual API endpoint and parameters
    # must match the model Space's current interface.
    try:
        client = Client(MODEL_SPACE)

        if image is not None:
            content = await image.read()
            suffix = os.path.splitext(image.filename or "image.png")[1]
            temp_path = "/tmp/shimul_upload" + suffix
            with open(temp_path, "wb") as f:
                f.write(content)

            result = await asyncio.to_thread(
                client.predict,
                prompt,
                handle_file(temp_path),
                api_name="/generate"
            )
        else:
            result = await asyncio.to_thread(
                client.predict,
                prompt,
                api_name="/generate"
            )

        return JSONResponse({"result": str(result)})

    except Exception as exc:
        raise HTTPException(
            502,
            "Video model request failed. Check the model API settings and free quota."
        ) from exc
