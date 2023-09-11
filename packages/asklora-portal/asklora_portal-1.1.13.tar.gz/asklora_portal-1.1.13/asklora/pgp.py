import json
import os
import traceback
from pathlib import Path
from typing import Any

import gnupg
from gnupg import _make_binary_stream, _threaded_copy_data, no_quote

from .exceptions.pgp import DecryptionError, EncryptionError, KeysError
from .logger import logger
from .singleton import SingletonMeta


class Result:
    data = None


class Gpg(gnupg.GPG):
    result = Result()

    def get_signature(self, data: str, to_bytes: bool = False) -> str | bytes:
        f = _make_binary_stream(data, self.encoding)
        args = ["--armor", "--output", "-", "--detach-sign"]
        fileobj = self._get_fileobj(f)
        try:
            p = self._open_subprocess(args)
            stdin = p.stdin
            writer = _threaded_copy_data(fileobj, stdin)
            stdout = p.stdout
            self._read_data(stdout, self.result)
            if to_bytes:
                return self.result.data
            return self.result.data.decode("ascii")
        finally:
            writer.join(0.01)
            if fileobj is not data:
                fileobj.close()

    def verify_file(self, signature, message, close_file=True, extra_args=None):
        "Verify the signature on the contents of the file-like object 'file'"
        result = self.result_map["verify"](self)
        args = ["--verify"]
        fs = _make_binary_stream(signature, self.encoding)
        fm = _make_binary_stream(message, self.encoding)

        if extra_args:
            args.extend(extra_args)
        import tempfile

        fd, fn = tempfile.mkstemp(prefix="pygpg-")
        sd, sn = tempfile.mkstemp(prefix="pygpg-")
        s = fs.read()
        m = fm.read()
        if close_file:
            fs.close()
            fm.close()
        os.write(fd, s)
        os.write(sd, m)
        os.close(fd)
        os.close(sd)
        args.append(no_quote(fn))
        args.append(no_quote(sn))
        try:
            p = self._open_subprocess(args)
            self._collect_output(p, result, stdin=p.stdin)
        finally:
            os.remove(fn)
            os.remove(sn)
        return result


class PGPHelper(metaclass=SingletonMeta):
    gpg = Gpg()

    def __init__(
        self,
        private_key_path: str | Path,
        public_key_path: str | Path,
        remote_public_key_path: str | Path,
    ) -> None:
        """Initialise the PGPHelper using key paths for Asklora private key, Asklora public key, and remote public key (can be for IBKR or DBS)

        Args:
            private_key_path (str | Path): Path to Asklora's private key
            public_key_path (str | Path): Path to Asklora's public key
            remote_public_key_path (str | Path): Path to the remote public key
        """

        self.private_key_path = private_key_path
        self.public_key_path = public_key_path
        self.remote_public_key_path = remote_public_key_path

        self.__load_keys()

    # UTILS
    def __raise_validation_error(self, message: str):
        logger.error(message)
        raise ValueError(message)

    def __raise_keys_error(self, message: str):
        logger.error(message)
        raise KeysError(message)

    def __raise_decryption_error(self, message: str):
        logger.error(message)
        raise DecryptionError(message)

    def __raise_encryption_error(self, message: str):
        logger.error(message)
        raise EncryptionError(message)

    def __load_keys(self):
        # setup keys
        try:
            keys = [
                ("private_key", self.private_key_path),
                ("public_key", self.public_key_path),
                ("remote_key", self.remote_public_key_path),
            ]

            for key in keys:
                name, path = key

                imported_key = self.gpg.import_keys_file(path)
                self.gpg.trust_keys(imported_key.fingerprints, "TRUST_ULTIMATE")

                setattr(self, name, imported_key.fingerprints[0])

            if len(self.private_key) > 1:
                self.private_key = self.private_key[0]

        except FileNotFoundError:
            self.__raise_keys_error("Cannot find keys")

    # DATA ACQUISITION
    def __get_payload_data(self, validated_payload: str | None):
        if not validated_payload:
            self.__raise_decryption_error("Payload is not valid")

        try:
            return validated_payload
        except Exception:
            self.__raise_decryption_error("Cannot get payload data")

    # VERIFICATION
    def __verify_payload(self, payload_data: str, key: str | None = None):
        signature_hash = self.gpg.get_signature(payload_data)
        try:
            return bool(
                self.gpg.verify_file(signature_hash, payload_data).status
                == "signature valid"
            )
        except Exception:
            self.__raise_decryption_error("Payload data is not verified")

    # DECRYPTION
    def __decrypt_data(self, payload_data: str) -> Any:
        try:
            decrypted_data = self.gpg.decrypt(
                payload_data,
                extra_args=["--default-key", self.private_key],
            )
            if not decrypted_data:
                raise Exception("Could not decrypt payload")

            return str(decrypted_data)
        except Exception:
            logger.error(decrypted_data.status)
            self.__raise_decryption_error("Cannot decrypt payload data")

    def __encrypt_data(self, message: str) -> str:
        if not isinstance(message, str):
            self.__raise_encryption_error("Message is not a string")

        try:
            pgp_message = self.gpg.encrypt(
                message,
                self.remote_key,
                sign=self.private_key,
                extra_args=[
                    "--cipher-algo",
                    no_quote("AES256"),
                    "--compress-algo",
                    no_quote("zip"),
                    "--digest-algo",
                    no_quote("SHA256"),
                ],
            )
            return str(pgp_message)
        except Exception as e:
            self.__raise_encryption_error(str(e) + "\n" + traceback.format_exc())

    def __encrypt_file(self, file: bytes, output: str | os.PathLike) -> str:
        try:
            encryption = self.gpg.encrypt_file(
                file,
                recipients=[self.remote_key],
                sign=self.public_key,
                armor=False,
                output=output,
                extra_args=["--batch"],
            )

            if not encryption.ok:
                raise Exception(f"Cannot encrypt file: {encryption.status}")

        except Exception as e:
            self.__raise_encryption_error(str(e) + "\n" + traceback.format_exc())

    def decrypt_payload(self, payload: str) -> dict:
        payload_data: str = self.__get_payload_data(payload)  # type: ignore

        verified = self.__verify_payload(payload_data)
        if not verified:
            self.__raise_validation_error("signature not valid")

        data: str = self.__decrypt_data(payload_data)
        return data

    def encrypt_payload(self, payload: str | dict) -> str:
        if isinstance(payload, dict):
            payload = json.dumps(payload)

        encrypted_data = self.__encrypt_data(payload)
        self.__verify_payload(encrypted_data)
        return encrypted_data

    def encrypt_file(self, file_path: str | os.PathLike, output: str | os.PathLike):
        try:
            with open(file_path, "rb") as file:
                self.__encrypt_file(file, output=output)

        except FileNotFoundError:
            logger.error("Cannot find file")
            raise EncryptionError("Cannot find file to encrypt")

        except EncryptionError as e:
            logger.error(f"Cannot encrypt file: {e}")
            raise

        except Exception as e:
            logger.error(f"Unhandled error: {e}")
            raise EncryptionError("Cannot encrypt file")
