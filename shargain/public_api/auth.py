from typing import Annotated

from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest
from django.middleware.csrf import get_token
from ninja import Router, Schema
from ninja.security import django_auth
from pydantic import AfterValidator
from pydantic.alias_generators import to_camel

from shargain.accounts.models import CustomUser
from shargain.offers.models import ScrappingTarget

# Create a separate router for auth endpoints (without requiring authentication)
auth_router = Router()


class BaseSchema(Schema):
    class Config:
        alias_generator = to_camel
        populate_by_name = True


class LoginRequest(BaseSchema):
    username: str
    password: str


def _validate_password(password: str):
    # TODO: Add proper validation from django validate_password
    return password


class SignupRequest(BaseSchema):
    email: str
    password: Annotated[str, AfterValidator(_validate_password)]


class UserSchema(BaseSchema):
    id: int
    username: str
    email: str


class LoginResponse(BaseSchema):
    success: bool
    message: str
    user: UserSchema | None = None


class CsrfTokenResponse(BaseSchema):
    csrf_token: str


@auth_router.get("/csrf", response=CsrfTokenResponse, auth=None, by_alias=True)
def get_csrf_token(request: HttpRequest):
    """Get CSRF token for login requests"""
    return CsrfTokenResponse(csrf_token=get_token(request))


@auth_router.post("/login", response=LoginResponse, auth=None, by_alias=True)
def login_view(request: HttpRequest, payload: LoginRequest):
    """Login endpoint that sets session cookie"""
    user = authenticate(username=payload.username, password=payload.password)
    if user is not None:
        login(request, user)
        return LoginResponse(success=True, message="Login successful", user=UserSchema.from_orm(user))
    else:
        return LoginResponse(success=False, message="Invalid credentials", user=None)


@auth_router.post("/signup", response=LoginResponse, auth=None, by_alias=True)
def signup_view(request: HttpRequest, payload: SignupRequest):
    """Signup endpoint that creates a user and logs them in"""
    if CustomUser.objects.filter(email=payload.email).exists():
        return LoginResponse(success=False, message="User with this email already exists", user=None)
    print(payload)
    user = CustomUser.objects.create_user(username=payload.email, email=payload.email, password=payload.password)

    ScrappingTarget.objects.create(owner=user)

    login(request, user)

    return LoginResponse(success=True, message="Signup successful", user=UserSchema.from_orm(user))


@auth_router.post("/logout", response=LoginResponse, by_alias=True)
def logout_view(request: HttpRequest):
    """Logout endpoint that clears session"""
    logout(request)
    return LoginResponse(success=True, message="Logout successful", user=None)


# Create a router for authenticated endpoints
router = Router(auth=django_auth)


@router.get("/me", response=UserSchema, operation_id="get_me", by_alias=True)
def get_current_user(request: HttpRequest):
    """Return the currently authenticated user"""
    return request.user
