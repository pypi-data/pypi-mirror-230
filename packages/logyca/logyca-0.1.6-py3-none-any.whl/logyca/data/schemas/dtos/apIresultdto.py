from logyca.data.schemas.dtos.tokensdto import TokensDTO
from logyca.data.schemas.dtos.apifilterexceptiondto import ApiFilterExceptionDTO
from typing import Any
from pydantic import BaseModel,Field

class APIResultDTO(BaseModel):
        resultToken:TokensDTO=Field(default=TokensDTO(),description="Gets or sets object with result")
        resultObject:Any=Field(default=None,description="Gets or sets object with result")
        apiException:ApiFilterExceptionDTO=Field(description="Gets or sets error")
        resultMessage:str=Field(default='',description="Gets or sets result of negative or positive message")
        dataError:bool=Field(default=True,description="Gets or sets a value indicating whether gets or sets a value if it is data error")
        class Config():
                orm_mode = True
        def __init__(self, **kwargs):
                kwargs['dataError'] = False
                kwargs['apiException'] = ApiFilterExceptionDTO()
                super().__init__(**kwargs)
