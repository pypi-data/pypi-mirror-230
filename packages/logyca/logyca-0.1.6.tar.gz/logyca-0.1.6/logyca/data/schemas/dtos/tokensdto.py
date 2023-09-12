from pydantic import BaseModel,Field

class TokensDTO(BaseModel):
    token:str=Field(default='',description="Gets or sets result Token")
    refreshToken:str=Field(default='',description="Gets or sets Refresh token")
    result:str=Field(default='',description="Gets or sets result request")
    emailActiveDirectory:str=Field(default='',description="Gets or sets email Active Directory")
    message:str=Field(default='',description="Gets or sets user message")
