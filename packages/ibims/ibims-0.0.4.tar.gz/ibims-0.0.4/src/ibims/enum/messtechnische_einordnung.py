"""
Messtechnische Einordnung ENUM
"""

from bo4e.enum.strenum import StrEnum


class MesstechnischeEinordnung(StrEnum):
    """
    An enum for the messtechnische Einordnung
    """

    IMS = "IMS"  #: Intelligentes Messsysteme
    KME_MME = "KME_MME"  #: Konventionelle Messeinrichtung / Moderne Messeinrichtung
    KEINE_MESSUNG = "KEINE_MESSUNG"
