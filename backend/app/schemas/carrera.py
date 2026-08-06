from pydantic import BaseModel, ConfigDict, Field


class CarreraCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)


class CarreraOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
