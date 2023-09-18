"""
extension of the official BO4E marktlokation
"""
from typing import Literal

from bo4e.bo.marktlokation import Marktlokation

from ibims.enum import MesstechnischeEinordnung, Regelzone


class MarktlokationErweitert(Marktlokation):
    """
    extension of the official BO4E marktlokation
    """

    messtechnische_einordnung: MesstechnischeEinordnung
    uebertragungsnetzgebiet: Regelzone
    variant: Literal["Z14", "Z15"]
    """
        gridUsageBilling.variant (Netznutzungsabrechnungsvariante)
            Z14: WorkPriceBasicPrice (Arbeitspreis/Grundpreis)
            Z15: WorkPricePerformancePrice (Arbeitspreis/Leistungspreis)
    """
    community_id: str
