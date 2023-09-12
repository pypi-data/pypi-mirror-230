from pydantic import BaseModel,Field
from logyca.data.enums.logycastatusenum import LogycaStatusEnum
from typing import Any
from http import HTTPStatus

class ApiFilterExceptionDTO(BaseModel):
        message:str=Field(default='',description="Gets or sets error message")
        isError:bool=Field(default=True,description="Gets or sets a value indicating whether api has error")
        detail:Any=Field(default=None,description="Gets or sets error detail")
        status:HTTPStatus=Field(default=HTTPStatus.OK,description="Gets or sets error code")
        logycaStatus:LogycaStatusEnum=Field(default=LogycaStatusEnum.Ok,description="Gets or sets error code")
        def __init__(self, **kwargs):
                kwargs['isError'] = False
                kwargs['message'] = ''
                kwargs['status'] = HTTPStatus.OK
                super().__init__(**kwargs)
