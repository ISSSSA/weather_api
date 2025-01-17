from pydantic import BaseModel


class AddCityRequest(BaseModel):
    user_id: int
    city: str
    lat: float
    lon: float


class RegisterUserRequest(BaseModel):
    username: str
