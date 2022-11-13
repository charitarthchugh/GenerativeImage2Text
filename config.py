from pydantic import BaseSettings


class Settings(BaseSettings):
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    twilio_user_name: str
    twilio_user_phone: str
    door_open: str
    
    
    class Config:
        env_file = ".env"
