"""Main execution point for Dice Backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient


from dice_be.exceptions import NotFoundHttpError
from dice_be.routers import games, users
from dice_be.models.users import NUser

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://dice-new.web.app'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(users.router)
app.include_router(games.router)

app.add_exception_handler(NotFoundHttpError, NotFoundHttpError.handler)

@app.on_event('startup')
async def startup_event():
    motor = AsyncMongoMockClient()
    await init_beanie(database=motor.db_name, document_models=[NUser])  # pyright: ignore


def custom_openapi():
    """Defines custom openapi parameters for Dice."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title='Dice',
        version='Pre-release',
        description='Dice Game',
        routes=app.routes,
    )
    openapi_schema['info']['x-logo'] = {
        'url': 'https://raw.githubusercontent.com/Koren13n/dice-fe/master/assets/images/dice_logo.png',
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

