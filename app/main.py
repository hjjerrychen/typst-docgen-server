import os
import sys

from fastapi import FastAPI
from signer.pdf_signer import PDFSigner
from pyhanko.sign import signers

from docgen.docgen import DocGen
from config.config import Config
from service.service import DocGenService


DEFAULT_CONFIG_PATHS = ["./config.toml", "/etc/secrets/config.toml"]

def main():
    config_path_env = os.getenv("CONFIG_PATH")
    config_path_arg = sys.argv[1] if len(sys.argv) > 1 else None
    
    config = Config([config_path_env, config_path_arg] + DEFAULT_CONFIG_PATHS).get_config()

    signer = PDFSigner(config.signer.private_key_path, config.signer.certificate_path, config.signer.root_certificate_path) if config.signer.enabled else None
    docgen = DocGen(config.assets.templates_dir, config.assets.fonts_dir, signer, config.metadata.author, config.metadata.creator, config.metadata.producer)
    server = FastAPI()
    service = DocGenService(server, docgen, config.server.api_key, signer=signer)

    service.start(config.server.host, config.server.port)


if __name__ == "__main__":
    main()
