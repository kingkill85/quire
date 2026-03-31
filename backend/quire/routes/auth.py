from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/api/auth/login")
async def login(request: Request, body: LoginRequest):
    verso = request.app.state.verso
    result = await verso.login(body.email, body.password)
    return result
