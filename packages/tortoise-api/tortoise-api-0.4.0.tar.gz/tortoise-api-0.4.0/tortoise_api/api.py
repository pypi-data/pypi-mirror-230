import logging
from os import getenv as env
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from tortoise.contrib.starlette import register_tortoise

from tortoise_api_model import Model
from tortoise_api.oauth import login_for_access_token, Token, get_current_user, reg_user
from tortoise_api.util import jsonify, delete, parse_qs


class Api:
    app: FastAPI
    models: {str: Model}

    def __init__(
        self,
        debug: bool = False,
        # auth_provider: AuthProvider = None, # todo: add auth
    ):
        """
        Parameters:
            debug: Debug SQL queries, api requests
            # auth_provider: Authentication Provider
        """
        self.routes: [APIRoute] = [
            APIRoute('/', self.api_menu),
            APIRoute('/model/{model}', self.all, methods=['GET']),
            APIRoute('/model/User', reg_user, methods=['POST']),
            APIRoute('/model/{model}', self.create, methods=['POST']),
            APIRoute('/{model}/{oid}', self.one_get, methods=['GET']),
            APIRoute('/{model}/{oid}', self.one_update, methods=['POST']),
            APIRoute('/{model}/{oid}', self.one_delete, methods=['DELETE']),
            APIRoute('/token', login_for_access_token, methods=['POST'], response_model=Token),
        ]
        self.debug = debug

    def start(self, models_module):
        self.models: {str: type[Model]} = {key: model for key in dir(models_module) if isinstance(model := getattr(models_module, key), type(Model)) and Model in model.mro()}
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
        self.app = FastAPI(debug=self.debug, routes=self.routes)
        load_dotenv()
        register_tortoise(self.app, db_url=env("DB_URL"), modules={"models": [models_module]}, generate_schemas=self.debug)
        return self.app


    # ROUTES
    async def api_menu(self, token: Annotated[str, Depends(get_current_user)]):
        return JSONResponse(list(self.models))


    async def create(self, request: Request, model: str):
        model: type[Model] = self.models.get(model)
        data = parse_qs(await request.body())
        obj: Model = await model.upsert(data)
        return RedirectResponse('/list/'+model.__name__, 303) # create # {True: 201, False: 202}[res[1]]

    async def all(self, model: str, limit: int = 50, page: int = 1):
        model: type[Model] = self.models.get(model)
        objects: [Model] = await model.all().prefetch_related(*model._meta.fetch_fields).limit(limit).offset(limit*(page-1))
        data = [await jsonify(obj) for obj in objects]
        return JSONResponse({'data': data}) # show all

    async def one_get(self, model: str, oid: int):
        model: type[Model] = self.models.get(model)
        obj = await model.get(id=oid).prefetch_related(*model._meta.fetch_fields)
        return JSONResponse(await jsonify(obj)) # show one

    async def one_update(self, request: Request, model: str, oid: int):
        model: type[Model] = self.models.get(model)
        data = parse_qs(await request.body())
        res = await model.upsert(data, oid)
        # return JSONResponse(await jsonify(res[0]), status_code=202) # update
        return RedirectResponse('/list/'+model.__name__, 303) # create # {True: 201, False: 202}[res[1]]

    async def one_delete(self, request: Request, model: str, oid: int):
        model: type[Model] = self.models.get(model)
        await delete(model, oid)
        return JSONResponse({}, status_code=202) # delete
