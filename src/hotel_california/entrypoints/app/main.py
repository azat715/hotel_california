from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.authentication import AuthenticationMiddleware

from hotel_california.config import get_settings
from hotel_california.entrypoints.app.auth_bearer import validate_token
from hotel_california.entrypoints.app.routers.admin import admin_router
from hotel_california.entrypoints.app.routers.auth import auth_router
from hotel_california.entrypoints.app.routers.rooms import rooms_router
from hotel_california.entrypoints.app.routers.users import users_router
from hotel_california.service_layer.exceptions import (
    AuthenticationError,
    BusinessLogicError,
)
from hotel_california.entrypoints.app.auth_session import SessionAuthBackend

settings = get_settings()

STATIC_DIR = str(settings.PATHS.fastapi_folder.joinpath(settings.PATHS.static_folder))

app = FastAPI(title=settings.APP_NAME)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    AuthenticationMiddleware, backend=SessionAuthBackend()
)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(rooms_router)
app.include_router(admin_router)


@app.exception_handler(BusinessLogicError)
async def logic_exception_handler(request: Request, exc: BusinessLogicError):
    return JSONResponse(
        status_code=422,
        content={"message": "Error! BusinessLogicError", "body": str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"message": "Error! ParseError", "body": exc.errors()},
    )


@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(request, exc):
    return JSONResponse(
        status_code=401,
        content={"message": "Error! AuthenticationError", "body": str(exc)},
    )


@app.get("/test")
async def test():
    return {"message": "Hello World"}


@app.get("/test_auth", dependencies=[Depends(validate_token)])
async def test_auth():
    return {"message": "Hello World"}
