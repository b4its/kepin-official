from __future__ import annotations

from typing import Literal
from pydantic import BaseModel


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
    tenants: list[dict] = []


PlanCode = Literal["free", "basic", "premium", "platinum"]


class CreateOrganizationRequest(BaseModel):
    name: str
    slug: str
    plan: PlanCode = "free"


class JoinOrganizationRequest(BaseModel):
    tenant_id: str
    join_code: str


class AuthUserResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: str = ""
    avatar_url: str = ""
    tenants: list[dict] = []
