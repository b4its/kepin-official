from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from kepin.api.dependencies import get_session
from kepin.core.ids import new_uuid

router = APIRouter(tags=["Dev Auth"])


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ProfileUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


DEV_USER = {
    "id": "dev-user-001",
    "email": "budi@tokomaju.com",
    "name": "Budi Santoso",
    "phone": "08123456789",
    "role": "owner",
    "avatarUrl": None,
}


@router.post("/register")
async def register(body: RegisterRequest, session: AsyncSession = Depends(get_session)):
    _ = session
    return {"id": new_uuid(), "email": body.email, "name": body.name}


@router.post("/login")
async def login(body: LoginRequest):
    _ = body
    return {"user": DEV_USER, "accessToken": "dev-token-simulasi", "authorizationEnabled": False}


@router.post("/logout")
async def logout():
    return {"success": True}


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest):
    _ = body
    return {"success": True, "message": "Email reset password terkirim (simulasi)"}


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest):
    _ = body
    return {"success": True}


@router.get("/profile")
async def get_profile():
    return {"user": DEV_USER, "authorizationEnabled": False}


@router.patch("/profile")
async def update_profile(body: ProfileUpdate):
    return {"user": {**DEV_USER, **body.model_dump(exclude_none=True)}}
