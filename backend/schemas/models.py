from pydantic import BaseModel, Field

MAX_CARACTERES = 20000

class TextoRequest(BaseModel):
    texto_a: str = Field(max_length=MAX_CARACTERES)
    texto_b: str = Field(max_length=MAX_CARACTERES)
    modo: str = "estrutural"
    limiar: float = Field(default=0.7, ge=0, le=1)
