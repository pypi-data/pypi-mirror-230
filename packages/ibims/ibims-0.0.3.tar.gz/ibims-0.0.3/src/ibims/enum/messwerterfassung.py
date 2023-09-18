"""
New ENUM to differentiate the data acquisition method in BO Zähler.
"""
from bo4e.enum.strenum import StrEnum


class Messwerterfassung(StrEnum):
    """
    Specify data acquisition method
    """

    FERNAUSLESBAR = "FERNAUSLESBAR"
    MANUELL_AUSGELESENE = "MANUELL_AUSGELESENE"
