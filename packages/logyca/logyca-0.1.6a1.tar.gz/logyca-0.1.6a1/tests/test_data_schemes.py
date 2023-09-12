from logyca import HealthEnum, LogycaStatusEnum, APIResultDTO, ApiFilterExceptionDTO, HTTPExceptionDTO, HealthDTO, TokensDTO

def test_health_dto():
    '''Description
    Checking the data types and the defined content of the enums
    '''
    listHealth=[]

    listHealth.append(HealthDTO(name='Check CPU',status=HealthEnum.Ok,description='OK'))
    listHealth.append(HealthDTO(name='Check Connect DB',status=HealthEnum.Warning,description='Warning'))
    listHealth.append(HealthDTO(name='Check Connect Storage',status=HealthEnum.Critical,description='Critical'))

    for item in listHealth:
        if (item.description=='OK'):
            assert item.status==0
        if (item.description=='Warning'):
            assert item.status==1
        if (item.description=='Critical'):
            assert item.status==2

def test_api_result():
    '''Description
    Checking the data types and schema structure
    '''
    tokensDTO=TokensDTO()
    tokensDTO.token='Token Example'

    apiFilterExceptionDTO=ApiFilterExceptionDTO()
    apiFilterExceptionDTO.isError=False
    apiFilterExceptionDTO.logycaStatus=LogycaStatusEnum.Already_Exists
    apiFilterExceptionDTO.status=LogycaStatusEnum.Already_Exists.mappingHttpStatusCode

    assert apiFilterExceptionDTO.logycaStatus == 6
    assert apiFilterExceptionDTO.status == 409

    httpExceptionDTO=HTTPExceptionDTO()
    httpExceptionDTO.detail='No Problem'

    listHealth=[]

    listHealth.append(HealthDTO(name='Check CPU',status=HealthEnum.Ok,description='OK'))
    listHealth.append(HealthDTO(name='Check Connect DB',status=HealthEnum.Warning,description='Warning'))
    listHealth.append(HealthDTO(name='Check Connect Storage',status=HealthEnum.Critical,description='Critical'))


    apiResultDTO=APIResultDTO()
    apiResultDTO.resultMessage=httpExceptionDTO.detail
    apiResultDTO.resultObject=listHealth
    apiResultDTO.dataError=False
    apiResultDTO.resultToken=tokensDTO
    apiResultDTO.apiException=apiFilterExceptionDTO

    for item in apiResultDTO.resultObject:
        if (item.description=='OK'):
            assert item.status==0
        if (item.description=='Warning'):
            assert item.status==1
        if (item.description=='Critical'):
            assert item.status==2

