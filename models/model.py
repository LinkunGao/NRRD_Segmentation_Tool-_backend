from pydantic import BaseModel


class Masks(BaseModel):
    caseId: str
    masks: object


class Mask(BaseModel):
    caseId: str
    sliceId: int
    label: str
    mask: list

