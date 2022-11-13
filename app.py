import os
import subprocess
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, UploadFile
from twilio.rest import Client

import config
from generativeimage2text import inference

app = FastAPI(title="whosthere backend")
settings = config.Settings()


load_dotenv()


@app.post("/")
async def whosthere(img: UploadFile):
    
        a = Path("image.jpg")
        a.write_bytes(img.file.read())
        caption = inference.test_git_inference_single_image(
            str(a.resolve()), "GIT_BASE_VATEX", ""
        )
        twilio_send_sms(caption)


@app.post("/sms")
def unlock(string: str):
    # body = request
    msg = body["body"]
    print(msg)
    if "y" in msg:
        settings.door_open = True


def twilio_send_sms(message: str):
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    return client.messages.create(
        from_=settings.twilio_phone_number, to=settings.twilio_user_phone, body=message
    )


@app.get("/door-status")
def check_door_status() -> bool:
    if settings.door_open == "True":
        return 1
    else:
        return 0


if __name__ == "__main__":
    os.environ["AZFUSE_TSV_USE_FUSE"] = "1"
    subprocess.run(
        [
            "python",
            "-m",
            "generativeimage2text.inference",
            "-p",
            """{'type': 'test_git_inference_single_image', 'image_path': 'aux_data/images/1.jpg', 'model_name': 'GIT_BASE_VATEX','prefix': '', }""",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # print(inference.test_git_inference_single_image(sys.argv[1], "GIT_BASE_VATEX", ""))
    uvicorn.run(app, port=8000, host="0.0.0.0")
