from pydantic import BaseModel,Field

class HTTPExceptionDTO(BaseModel):
    detail:str=Field(default='',description="HTTPException")
