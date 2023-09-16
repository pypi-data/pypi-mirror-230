from __future__ import annotations

import re
from dataclasses import dataclass


class InvalidWellLabelError(ValueError):
    """Invalid well label error"""


@dataclass
class WellPosition:
    """Dataclass to represent well position for a well in a plate reader"""

    row: int
    column: int

    @staticmethod
    def _parse_letter_to_index(char: str) -> int:
        """
        This function takes a single letter string and turns it into an index.

        The string must be in A-Z or a-z.
        """

        if char.isupper():
            # Map A-Z to 1-26
            return 1 + ord(char) - ord("A")
        # Map a-z to 27-52
        return 27 + ord(char) - ord("a")

    @staticmethod
    def from_well_label(well_label: str) -> WellPosition:
        """
        For an alphanumeric well_label, return the corresponding well position.
        A well_label must satisfy following conditions:
        1. It must start with a letter
        2. It can contain at max two letters
            - When it contains two letters, they must both be upper case
        3. Letter(s) my be followed by at least one and at max two digits

        If the label cannot be parsed, `InvalidWellLabelError` is raised.

        Parsing for well_label containing single letter is case sensitive.
        ie. well labels A02 and a02 represent different wells on the plate

        And Parsing for well_label containing two letters is limited to uppercase only.
        ie. AB01 is supported but ab01, Ab01 and aB01 are not supported

        The following are the only supported sequence of rows for a plate

        1. A -> Z then a -> z
        2. A -> Z then AA -> AZ

        Args:
            well_label (str): Alphanumeric string representing the well label.

        Returns:
            WellPositions: Return the corresponding WellPosition for well_label. eg:
            A01 -> WellPosition(row=1, column=1)
            A45 -> WellPosition(row=1, column=45)
            Z12 -> WellPosition(row=26, column=12)
            a12 -> WellPosition(row=27, column=12)
            z34 -> WellPosition(row=62, column=34)
            BD34 -> WellPosition(row=56, column=34)
            AA01 -> WellPosition(row=27, column=34)
        """

        single_letter_pattern = r"^[a-zA-Z]{1,1}\d{1,2}$"
        two_letter_pattern = r"^[A-Z]{2,2}\d{1,2}$"

        if re.match(single_letter_pattern, well_label):
            row = WellPosition._parse_letter_to_index(well_label[0])
            return WellPosition(row, int(well_label[1:]))
        if re.match(two_letter_pattern, well_label):
            row_p0 = WellPosition._parse_letter_to_index(well_label[0])
            row_p1 = WellPosition._parse_letter_to_index(well_label[1])
            return WellPosition(row_p0 * 26 + row_p1, int(well_label[2:]))

        raise InvalidWellLabelError(
            f"Well label {well_label} can't be parsed. "
            "It must match one of the following patterns: "
            f"{single_letter_pattern} or {two_letter_pattern}"
        )
