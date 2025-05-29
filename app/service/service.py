import os
import uuid
import secrets
from git import Optional
import uvicorn

from fastapi import FastAPI, HTTPException, Response, Depends, UploadFile, status
from fastapi.security import APIKeyHeader

from signer.pdf_signer import PDFSigner
from docgen.docgen import DocGen
from config.config import DocGenConfig
from service.auth import Auth
from service.types import RenderRequestBody


class DocGenService:
    def __init__(self, server: FastAPI, docgen: DocGen, api_key: str, signer: Optional[PDFSigner] = None):
        self.docgen = docgen
        self.server = server
        self.signer = signer
        self.auth = Auth(api_key)
        self._register_routes()

    def _register_routes(self):  
        self.server.router.add_api_route("/render/{template_id}/{version}", self.render, methods=["POST"])
        self.server.router.add_api_route("/", self.root, methods=["GET"])
        if self.signer:
            self.server.router.add_api_route("/verify/pdf", self.verify_pdf, methods=["POST"])

    async def root(self):
        return {"status": "ok",
                "message": "This is an official website of the Government of Jerryville."}

    def render(self, template_id: str, version: str, body: RenderRequestBody, api_key: str = Depends(Auth.HEADER_PARSER)):
        request_id = str(uuid.uuid4())
        if not self.auth.verify_api_key(api_key):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        try: 
            data = self.docgen.generate(template_id, version, body.data, body.allow_print or False)
            headers = {'Content-Disposition': f'inline; filename="{request_id}.pdf"'}
            return Response(data, media_type='application/pdf', headers=headers)
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
        
    def verify_pdf(self, file: UploadFile):
        if not self.signer:
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="PDF signing is not enabled in the configuration.")
        
        try:
            pdf_data = file.file.read()
            if not self.signer.verify(pdf_data):
                return {"valid": False, "message": "Invalid PDF signature"}
            return {"valid": True, "message": "PDF signature is valid"}
        except Exception as e:
            print(f"Error verifying PDF: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    def start(self, host: str, port: int):
        uvicorn.run(self.server, host=host, port=port)