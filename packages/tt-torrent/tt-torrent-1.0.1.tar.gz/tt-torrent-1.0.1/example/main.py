import sys
import asyncio
from termcolor import colored
from tttorrent.new.client import NewClient


async def main() -> None:
    client = NewClient(email="extra_pamoon@hotmail.com", password="Wijittar8611")
    creds = await client.auth()
    if not creds:
        sys.exit(print(colored("[ERROR]: Something wrong has happpened while authenticate", "red")))
    with open("/workspace/content/1/description.txt", "r") as f:
        description = f.read()
        f.close()
    url = await client.upload(
        category=60,
        torrent_path="/workspace/content/1/IObit Driver Booster Pro 11.0.0.21 + Crack.iso.torrent",
        image_path="/workspace/content/1/img.jpg",
        description=description,
    )
    print(url)
    client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
