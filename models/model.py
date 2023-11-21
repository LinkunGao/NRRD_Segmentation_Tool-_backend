from pydantic import BaseModel


class Masks(BaseModel):
    caseId: str
    masks: object


class Mask(BaseModel):
    caseId: str
    sliceId: int
    label: str
    mask: list


class Sphere(BaseModel):
    caseId: str
    sliceId: int
    origin: list
    spacing: list
    sphereRadiusPixel: int
    sphereOriginPixel: list
