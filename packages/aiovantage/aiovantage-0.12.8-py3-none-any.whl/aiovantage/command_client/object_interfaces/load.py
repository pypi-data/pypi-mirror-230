"""Interface for querying and controlling loads."""

from enum import IntEnum
from typing import Optional, Sequence

from .base import Interface


class LoadInterface(Interface):
    """Interface for querying and controlling loads."""

    class RampType(IntEnum):
        """The type of ramp to perform."""

        STOP = 2
        OPPOSITE = 3
        DOWN = 4
        UP = 5
        FIXED = 6
        VARIABLE = 7
        ADJUST = 8

    async def turn_on(
        self,
        vid: int,
        transition: Optional[float] = None,
        level: Optional[float] = None,
    ) -> None:
        """Turn on a load.

        Args:
            vid: The Vantage ID of the load.
            transition: The time in seconds to transition to the new level, defaults to immediate.
            level: The level to set the load to (0-100), defaults to 100.
        """
        if level is None:
            level = 100

        if transition is None:
            return await self.set_level(vid, level)

        await self.ramp(vid, level, transition)

    async def turn_off(self, vid: int, transition: Optional[float] = None) -> None:
        """Turn off a load.

        Args:
            vid: The Vantage ID of the load.
            transition: The time in seconds to ramp the load down.
        """
        if transition is None:
            return await self.set_level(vid, 0)

        await self.ramp(vid, 0, transition)

    async def set_level(self, vid: int, level: float) -> None:
        """Set the level of a load.

        Args:
            vid: The Vantage ID of the load.
            level: The level to set the load to (0-100).
        """
        # Clamp level to 0-100
        level = max(min(level, 100), 0)

        # INVOKE <id> Load.SetLevel <level (0-100)>
        # -> R:INVOKE <id> <rcode> Load.SetLevel <level (0-100)>
        await self.invoke(vid, "Load.SetLevel", level)

    async def get_level(self, vid: int) -> float:
        """Get the level of a load.

        Args:
            vid: The Vantage ID of the load.

        Returns:
            The level of the load, as a percentage (0-100).
        """
        # INVOKE <id> Load.GetLevel
        # -> R:INVOKE <id> <level (0-100)> Load.GetLevel
        response = await self.invoke(vid, "Load.GetLevel")
        level = float(response.args[1])

        return level

    async def ramp(
        self,
        vid: int,
        level: float,
        seconds: float,
        ramp_type: RampType = RampType.FIXED,
    ) -> None:
        """Ramp a load to a level over a number of seconds.

        Args:
            vid: The Vantage ID of the load.
            level: The level to ramp the load to (0-100).
            seconds: The number of seconds to ramp the load over.
            ramp_type: The type of ramp to perform.
        """
        # INVOKE <id> Load.Ramp <type> <seconds> <level>
        # -> R:INVOKE <id> <rcode> Load.Ramp <type> <seconds> <level>
        await self.invoke(vid, "Load.Ramp", ramp_type, seconds, level)

    @classmethod
    def parse_get_level_status(cls, args: Sequence[str]) -> float:
        """Parse a 'Load.GetLevel' event.

        Args:
            args: The arguments of the event.

        Returns:
            The level of the load.
        """
        # ELLOG STATUS ON
        # -> EL: <id> Load.GetLevel <level (0-100000)>
        # ADDSTATUS <id>
        # -> S:STATUS <id> Load.GetLevel <level (0-100000)>
        return float(args[0]) / 1000
