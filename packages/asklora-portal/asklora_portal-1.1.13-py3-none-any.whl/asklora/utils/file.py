import hashlib
from pathlib import Path

from asklora.logger import logger


def get_file_size(file: Path | str) -> int | None:
    file_path = Path(file) if isinstance(file, str) else file

    try:
        return file_path.stat().st_size
    except FileNotFoundError:
        logger.error(f"Cannot find file: {file}")
        return None
    except Exception as e:
        logger.error(f"Unhandled error when accessing {file}: {e}")
        return None


def get_file_sha1(file: str) -> str | None:
    h = hashlib.sha1()

    try:
        with open(file, "rb") as f:
            while True:
                chunk = f.read(h.block_size)

                if not chunk:
                    break

                h.update(chunk)
        return h.hexdigest()

    except FileNotFoundError:
        logger.error(f"Cannot find file: {file}")
        return None
    except Exception as e:
        logger.error(f"Unhandled error when accessing {file}: {e}")
        return None
