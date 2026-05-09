from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DocType(str, Enum):
    GUIDELINE = "guideline"
    TRIAL = "trial"
    DRUG_LABEL = "drug_label"
    ABSTRACT = "abstract"
    DOSSIER = "dossier"


class Agency(str, Enum):
    EMA = "EMA"
    GBA = "G-BA"
    HAS = "HAS"
    NICE = "NICE"
    AIFA = "AIFA"
    CBG = "CBG"
    OTHER = "OTHER"


class Country(str, Enum):
    AT = "AT"
    BE = "BE"
    BG = "BG"
    CY = "CY"
    CZ = "CZ"
    DE = "DE"
    DK = "DK"
    EE = "EE"
    ES = "ES"
    FI = "FI"
    FR = "FR"
    GR = "GR"
    HR = "HR"
    HU = "HU"
    IE = "IE"
    IT = "IT"
    LT = "LT"
    LU = "LU"
    LV = "LV"
    MT = "MT"
    NL = "NL"
    PL = "PL"
    PT = "PT"
    RO = "RO"
    SE = "SE"
    SI = "SI"
    SK = "SK"
    UK = "UK"
    EU = "EU"
    OTHER = "OTHER"


class ChunkMetadata(BaseModel):
    text: str = Field(...)
    chunk_index: int = Field(default=0)
    chunk_id: str = Field(default="")
    doc_id: str = Field(default="")
    source: str = Field(default="unknown")
    doc_type: DocType = Field(default=DocType.ABSTRACT)
    agency: Agency = Field(default=Agency.OTHER)
    country: Country = Field(default=Country.OTHER)
    date: str = Field(default="")
    pmid: Optional[str] = Field(default=None)
    nct_id: Optional[str] = Field(default=None)
    drug_name: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)

    class Config:
        use_enum_values = True
