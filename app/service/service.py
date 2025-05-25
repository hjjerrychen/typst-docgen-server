import os
import uuid
import secrets
import uvicorn

from fastapi import FastAPI, HTTPException, Response, Depends, status
from fastapi.security import APIKeyHeader

from docgen.docgen import DocGen
from config.config import DocGenConfig
from service.auth import Auth
from service.types import RenderRequestBody


class DocGenService:
    def __init__(self, server: FastAPI, docgen: DocGen, api_key: str):
        self.docgen = docgen
        self.server = server
        self.auth = Auth(api_key)
        self._register_routes()

    def _register_routes(self):  
        self.server.router.add_api_route("/render/{template_id}/{version}", self.render, methods=["POST"])
        self.server.router.add_api_route("/", self.root, methods=["GET"])

    async def root(self):
        return {"status": "ok",
                "message": "This is an official website of the Government of Jerryville."}

    async def render(self, template_id: str, version: str, body: RenderRequestBody, api_key: str = Depends(Auth.HEADER_PARSER)):
        request_id = str(uuid.uuid4())
        if not self.auth.verify_api_key(api_key):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        try: 
            data = self.docgen.generate(template_id, version, body.data)
            headers = {'Content-Disposition': f'inline; filename="{request_id}.pdf"'}
            return Response(data, media_type='application/pdf', headers=headers)
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    def start(self, host: str, port: int):
        uvicorn.run(self.server, host=host, port=port)