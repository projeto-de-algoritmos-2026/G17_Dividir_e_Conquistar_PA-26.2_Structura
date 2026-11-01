from pydantic import BaseModel

class TextoRequest(BaseModel):
    texto_a: str
    texto_b: str