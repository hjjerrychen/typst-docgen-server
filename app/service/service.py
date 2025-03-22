import uvicorn
import os
import uuid
from fastapi import FastAPI, HTTPException, Response

from docgen.docgen import DocGen
from config.config import DocGenConfig

from service.types import RenderRequestBody


class DocGenService:
    def __init__(self, server: FastAPI, docgen: DocGen):
        self.docgen = docgen
        self.server = server
        self._register_routes()

    def _register_routes(self):  
        self.server.router.add_api_route("/render/{template_id}/{version}", self.render, methods=["POST"])
        self.server.router.add_api_route("/", self.root, methods=["GET"])

    async def root(self):
        return {"status": "ok",
                "message": "This is an official website of the Government of Jerryville."}

    async def render(self, template_id: str, version: str, body: RenderRequestBody):
        id = str(uuid.uuid4())
        try: 
            data = self.docgen.generate(template_id, version, body.data)
            headers = {'Content-Disposition': f'inline; filename="{id}.pdf"'}
            return Response(data, media_type='application/pdf', headers=headers)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def start(self, host: str, port: int):
        uvicorn.run(self.server, host=host, port=port)