from __future__ import annotations

from datetime import datetime
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
    access_token: str | None = None
    token_type: str = "bearer"
    user: dict | None = None
    tenants: list[dict] = []
    mfa_required: bool = False
    mfa_token: str | None = None


class MfaVerifyRequest(BaseModel):
    mfa_token: str
    code: str


class MfaSetupResponse(BaseModel):
    secret: str
    otpauth_uri: str


class MfaEnableRequest(BaseModel):
    code: str


class MfaEnableResponse(BaseModel):
    recovery_codes: list[str]


class MfaDisableRequest(BaseModel):
    code: str


class MfaStatusResponse(BaseModel):
    enabled: bool = False
    setup_at: datetime | None = None


class ForgotPasswordRequest(BaseModel):
    email: str


class ForgotPasswordResponse(BaseModel):
    message: str
    dev_reset_token: str | None = None


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


PlanCode = Literal["free", "basic", "premium", "platinum"]


class CreateOrganizationRequest(BaseModel):
    name: str
    slug: str
    plan: PlanCode = "free"


class JoinOrganizationRequest(BaseModel):
    tenant_id: str
    join_code: str


class JoinByCodeRequest(BaseModel):
    join_code: str


class RegenerateJoinCodeRequest(BaseModel):
    tenant_id: str


class AuthUserResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: str = ""
    avatar_url: str = ""
    is_superadmin: bool = False
    tenants: list[dict] = []
