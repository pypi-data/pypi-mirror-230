import os
import re
import sys
import shutup
import asyncio
import argparse
from pathlib import Path
from termcolor import colored
from tttorrent.new.client import NewClient

# used to hide annoying warning
shutup.please()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="tt-torrent",
        usage="tt-torrent [-m] [-r] [-c] [-e] [-p] [-w]",
        epilog=colored("😈 Thanks for use %(prog)s!", "magenta"),
        description=colored(
            "😈 Daemon to manage torrents through tt-torrent website.",
            "magenta",
        ),
    )

    parser.add_argument(
        "-e",
        "--email",
        type=str,
        required=True,
        help="tt-torrent account email",
    )

    parser.add_argument(
        "-p",
        "--password",
        type=str,
        required=True,
        help="tt-torrent account password",
    )

    parser.add_argument(
        "-t",
        "--torrent",
        type=str,
        help="Path to log or vault, folder or file",
    )

    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        help="What do you want to do",
    )

    parser.add_argument(
        "-w",
        "--where",
        type=str,
        help="For -r mode only, -w flag does check for files to upload in specified path",
    )

    parser.add_argument(
        "-c",
        "--category",
        type=int,
        help="Upload to any specified category",
    )

    parser.add_argument(
        "-r",
        "--recursive",
        type=str,
        help="Iterate over all files in the specified path",
    )

    args = parser.parse_args()
    ay = asyncio.get_event_loop()
    client = NewClient(email=args.email, password=args.password)
    creds = ay.run_until_complete(client.auth())
    if not creds:
        sys.exit(print(colored("[ERROR]: Something wrong has happpened while authenticate", "red")))
    if args.mode == "upload":
        if args.recursive == "yes":
            for root, dirs, files in os.walk(args.where):
                torrent_path = ""
                image_path = ""
                description = ""
                for dir in dirs:
                    subf = os.path.join(root, dir)
                    for file in os.listdir(subf):
                        if re.match(r".*\.torrent$", file):
                            torrent_path += os.path.join(subf, file)
                        elif re.match(r".*\.txt$", file):
                            with open(os.path.join(subf, file), "r") as f:
                                description += f.read()
                                f.close()
                        elif re.match(r".*\.(jpg|jpeg|png)$", file):
                            image_path += os.path.join(subf, file)
                    url = ay.run_until_complete(
                        client.upload(
                            category=args.category,
                            torrent_path=torrent_path,
                            image_path=image_path,
                            description=description,
                        )
                    )
            print(url)
            client.close()
