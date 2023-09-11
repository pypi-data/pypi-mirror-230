import tempfile
from base64 import b64decode, b64encode
from os import PathLike
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from asklora.brokerage import models
from asklora.logger import logger
from asklora.pgp import PGPHelper
from asklora.utils.common import deep_get


class DAM:
    @classmethod
    def __process_zip_file(cls, files: str, path: Path, file_name="data.zip"):
        zip_file = path.joinpath(file_name)

        with ZipFile(zip_file, "w", ZIP_DEFLATED) as zf:
            for file in files:
                file = Path(file) if isinstance(file, str) else file
                zf.write(file, file.name)

        return zip_file

    @classmethod
    def __encode_file(cls, file_path: Path) -> str | None:
        try:
            file_data = file_path.read_bytes()

            # encode the data to base64
            encoded_data = b64encode(file_data)

            return encoded_data.decode("utf-8").replace("\n", "")

        except FileNotFoundError:
            logger.error("Cannot find file")
        except Exception as e:
            logger.error(f"Cannot encode zip file: {e}")

    @classmethod
    def __encrypt_and_encode_file(
        cls,
        file: Path,
        pgp_helper: PGPHelper,
    ) -> str:
        encrypted_file = file.parent.joinpath(f"encrypted_{file.name}")

        pgp_helper.encrypt_file(file, output=encrypted_file)
        return cls.__encode_file(encrypted_file)

    @classmethod
    def encode_file_payload(
        cls,
        file_content: str,
        file_name: str,
        pgp_helper: PGPHelper,
        archived: bool = False,
        attached_files: list[str | PathLike] | None = None,
    ):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            payload_file = tmp_path.joinpath(file_name)

            # write file content
            payload_file.write_text(file_content)

            if archived or attached_files:
                files = [payload_file]

                if isinstance(attached_files, list):
                    files.extend(attached_files)

                payload_file = cls.__process_zip_file(
                    files=files,
                    path=tmp_path,
                    file_name="data.zip",
                )

            # encrypt the file and encode it to base64
            encoded_file = cls.__encrypt_and_encode_file(
                payload_file,
                pgp_helper=pgp_helper,
            )

            return encoded_file

    @classmethod
    def generate_application_payload(
        cls,
        data: models.DAMApplicationPayload,
        pgp_helper: PGPHelper,
        xml_file_name: str = "application.xml",
    ):
        xml_data = data.generate_application_xml()
        attached_files = data.attached_files

        logger.debug(f"Payload:\n{xml_data}")

        return cls.encode_file_payload(
            xml_data,
            file_name=xml_file_name,
            pgp_helper=pgp_helper,
            attached_files=attached_files,
        )

    @classmethod
    def decode_response(cls, data: str, pgp_helper: PGPHelper):
        encrypted_data = b64decode(data.encode())
        data = pgp_helper.decrypt_payload(encrypted_data)

        return data

    @classmethod
    def handle_eca_response(cls, response: dict, pgp_helper: PGPHelper):
        xml_data = cls.decode_response(
            deep_get(response, ["fileData", "data"]),
            pgp_helper=pgp_helper,
        )
        dict_data = models.Process.from_xml(xml_data.encode()).dict(exclude_none=True)
        response["fileData"]["data"] = dict_data

        return response
