from io import BytesIO
import os
import secrets

from git import Optional
from signer.pdf_signer import PDFSigner
from docgen.utils import Version
from docgen.templates import Template, TemplateResolver
from docgen.typst import Typst

import pikepdf

from pyhanko.sign import signers
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter

class DocGen:
    def __init__(self, templates_dir: str, fonts_dir: list[str], signer: Optional[PDFSigner], author: str, creator: str, producer: str):
        if not os.path.isdir(templates_dir):
            raise NotADirectoryError(
                f"Templates directory '{templates_dir}' does not exist."
            )
        for font_dir in fonts_dir:
            if not os.path.isdir(font_dir):
                raise NotADirectoryError(
                    f"Fonts directory '{font_dir}' does not exist."
                )
                # template resolver needs to check more things
        self.templates: dict[str, Template] = TemplateResolver(templates_dir).resolve()
        self.fonts_dir = fonts_dir
        self.signer = signer
        self.author = author
        self.creator = creator
        self.producer = producer

    def generate(
        self,
        template_id: str,
        version: str,
        data: dict,
        allow_print: bool
    ):
        if not self._template_id_exists(template_id):
            raise ValueError(f"Template '{template_id}' does not exist.")
        if not self._version_exists(template_id, version):
            raise ValueError(
                f"Version '{version}' does not exist for template '{template_id}'."
            )

        extra_params = self._check_extra_params(template_id, version, data)
        if len(extra_params) > 0:
            raise TypeError(
                f"Extra parameters for version '{version}' of template '{template_id}' are provided: {', '.join(extra_params)}"
            )

        missing_params = self._check_required_params(template_id, version, data)
        if len(missing_params) > 0:
            raise TypeError(
                f"Required parameters for version '{version}' of template '{template_id}' are missing: {', '.join(missing_params)}"
            )

        pdf: bytes = Typst.render(
            self.templates[template_id].get_path(version), self.fonts_dir, data
        )
        owner_pwd = secrets.token_urlsafe(16)
        pdf = self._set_metadata_security(pdf, allow_print, template_id, version, owner_pwd)
        if not self.signer:
            return pdf
        return self.signer.sign(pdf, owner_pwd=owner_pwd)

    def _set_metadata_security(
        self, pdf: bytes, allow_print: bool, name: str, version: str, owner_pwd: str
    ) -> bytes:
        with BytesIO(pdf) as pdf_buffer:
            pdf = pikepdf.open(pdf_buffer)
            output_stream = BytesIO()

            pdf.docinfo["/Title"] = f"{name} (v{version})"
            pdf.docinfo["/Author"] = self.author
            pdf.docinfo["/Creator"] = f"{self.creator} (Rev. {Version.get_git_hash_version()})"
            pdf.docinfo["/Producer"] = f"{self.producer} (Rev. {Version.get_git_hash_version()})"

            pdf.save(
                output_stream,
                encryption=pikepdf.Encryption(
                    owner=owner_pwd,
                    allow=pikepdf.Permissions(
                        modify_annotation=False,
                        modify_assembly=False,
                        modify_form=False,
                        modify_other=False,
                        accessibility=False,
                        extract=False,
                        print_lowres=allow_print,
                        print_highres=allow_print,
                    )
                )
            )
            return output_stream.getvalue()

    def _template_id_exists(self, template_id: str):
        return template_id in self.templates

    def _version_exists(self, template_id: str, version: str):
        return self.templates[template_id].has_version(version)

    def _check_required_params(self, template_id: str, version: str, data: dict):
        return list(
            set(self.templates[template_id].get_required_params(version)).difference(
                data.keys()
            )
        )

    def _check_extra_params(self, template_id: str, version: str, data: dict):
        return list(
            set(data.keys()).difference(
                self.templates[template_id].get_required_params(version)
            )
        )
