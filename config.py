from pydantic import BaseModel, Field

class LoadConfig(BaseModel):
    str_strip_whitespace: bool = Field(default=True)
    str_min_length: int = Field(default=1)

    class Config:
        from_attributes = True
