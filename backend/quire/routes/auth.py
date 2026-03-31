from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/api/auth/login")
async def login(request: Request, body: LoginRequest):
    verso = request.app.state.verso
    try:
        result = await verso.login(body.email, body.password)
        return result
    except Exception as e:
        return JSONResponse(
            status_code=401,
            content={"error": str(e)},
        )
