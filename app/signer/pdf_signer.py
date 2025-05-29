from io import BytesIO
from typing import Optional

from pyhanko.sign import signers
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.keys import load_cert_from_pemder
from pyhanko_certvalidator import ValidationContext
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature

class PDFSigner:
    def __init__(self, private_key_path: str, certificate_path: str):
        self.validation_context = ValidationContext(trust_roots=[load_cert_from_pemder(certificate_path)])
        self.signer = signers.SimpleSigner.load(private_key_path, certificate_path)
        if not self.signer:
            raise ValueError("Signer could not be initialized with the provided key and certificate.")

    def sign(self, pdf: bytes, owner_pwd: Optional[str] = None) -> bytes:
        with BytesIO(pdf) as pdf_buffer:
            w = IncrementalPdfFileWriter(pdf_buffer)
            if owner_pwd:
                w.encrypt(owner_pwd)
            out = signers.PdfSigner(
                signers.PdfSignatureMetadata(field_name='JerryvilleGovernmentIssuerSignature'),
                signer=self.signer,
            ).sign_pdf(w)
            return out.read()

    def verify(self, pdf: bytes) -> tuple[bool, str]:
        with BytesIO(pdf) as pdf_buffer:
            r = PdfFileReader(pdf_buffer)
            # r.decrypt()
            sig = r.embedded_signatures[0]
            
            status = validate_pdf_signature(sig, self.validation_context)
            return status.bottom_line, status.pretty_print_details()
