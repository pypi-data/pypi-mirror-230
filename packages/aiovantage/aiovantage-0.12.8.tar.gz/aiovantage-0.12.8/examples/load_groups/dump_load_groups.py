"""Prints out the id, name, and members of each load group in the Vantage controller."""

import argparse
import asyncio
import contextlib
import logging

from aiovantage import Vantage

# Grab connection info from command line arguments
parser = argparse.ArgumentParser(description="aiovantage example")
parser.add_argument("host", help="hostname of Vantage controller")
parser.add_argument("--username", help="username for Vantage controller")
parser.add_argument("--password", help="password for Vantage controller")
parser.add_argument("--debug", help="enable debug logging", action="store_true")
args = parser.parse_args()


async def main() -> None:
    """Run code example."""
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    # Connect to the Vantage controller
    async with Vantage(args.host, args.username, args.password) as vantage:
        # Print out the id, name, and members of each load group
        async for load_group in vantage.load_groups:
            print(
                f"[{load_group.id}] '{load_group.name}' loads={load_group.load_ids} level={load_group.level}%"
            )


with contextlib.suppress(KeyboardInterrupt):
    asyncio.run(main())
