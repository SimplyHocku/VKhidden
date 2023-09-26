import random
import asyncio
import aiofiles
from os import unlink, listdir

import cryptography.fernet
from cryptography.fernet import Fernet
from pathlib import PurePath, Path


async def _check_key_exists():
    path = Path("keys")
    return True if listdir(path) else False


async def create_key(name):
    path = Path("keys")
    name = name.replace(name, f"{name}.key")
    direct = listdir(path)

    key = Fernet.generate_key()
    if direct:
        [unlink(f) for f in path.iterdir()]
    save_file = Path(path, name)
    with open(save_file, "wb") as r_key:
        r_key.write(key)

    return 200 if save_file.exists() else 400


async def encrypt_message(msg):
    path = Path("keys")

    file = next(path.iterdir())
    async with aiofiles.open(file, "rb") as f:
        key = await f.read()
        cipher = Fernet(key)
        crypt_msg = cipher.encrypt(bytes(msg, encoding="utf-8"))
        return crypt_msg


async def _decrypt_message(msg):
    path = Path("keys")
    file = next(path.iterdir())
    async with aiofiles.open(file, "rb") as f:
        msg = bytes(msg[2:], encoding="utf-8")
        key = await f.read()
        cipher = Fernet(key)
        try:
            decrypted_msg = cipher.decrypt(msg).decode("utf-8")
        except cryptography.fernet.InvalidToken:
            return 400
        return decrypted_msg


# asyncio.run(c)
