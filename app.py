import os
import subprocess
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile
from twilio.rest import Client

import config
from generativeimage2text import inference

app = FastAPI(title="whosthere backend")
settings = config.Settings()


load_dotenv()


@app.post("/")
async def unlock_door(file: UploadFile):
    if "image" in file.content_type:
        a = Path("image.jpg")
        a.write_bytes(file.file.read())
        caption = inference.test_git_inference_single_image(
            a.resolve(), "GIT_BASE_VATEX", ""
        )
        user_response = twilio_send_sms(caption)
        if user_response:
            pass


def twilio_send_sms(to_number: str, message: str):
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    return client.messages.create(
        from_=settings.twilio_phone_number, to=to_number, body=message
    )


@app.post("/update-user")
def update_user(number: int, name: str):
    pass


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
    # uvicorn.run(app)
