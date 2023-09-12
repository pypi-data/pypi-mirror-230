<p align="center">
  <a href="https://logyca.com/"><img src="https://logyca.com/wp-content/uploads/2019/06/logo-logyca.png" alt="Logyca"></a>
</p>
<p align="center">
    <em>LOGYCA public libraries</em>
</p>

<p align="center">
<a href="https://pypi.org/project/logyca" target="_blank">
    <img src="https://img.shields.io/pypi/v/logyca?color=orange&label=PyPI%20Package" alt="Package version">
</a>
<a href="(https://www.python.org" target="_blank">
    <img src="https://img.shields.io/badge/Python-%5B%3E%3D3.7%2C%3C%3D3.11%5D-orange" alt="Python">
</a>
</p>


---

# About us

* <a href="http://logyca.com" target="_blank">LOGYCA Company</a>
* <a href="https://www.youtube.com/channel/UCzcJtxfScoAtwFbxaLNnEtA" target="_blank">LOGYCA Youtube Channel</a>
* <a href="https://www.linkedin.com/company/logyca" target="_blank"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="Linkedin"></a>
* <a href="https://twitter.com/LOGYCA_Org" target="_blank"><img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" alt="Twitter"></a>
* <a href="https://www.facebook.com/OrganizacionLOGYCA/" target="_blank"><img src="https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white" alt="Facebook"></a>

---

# What's libraries

* **Traversal libraries**: Standard methods to be used by microservices.
* **Return codes**: Standard methods to report result status codes.
* **Monitoring**: Standard methods to report check health status codes.
* **Helpers**: Standard methods to be used. *

---

# Semantic Versioning

logyca <MAJOR>.<MINOR>.<PATCH>

* **MAJOR**: version when you make incompatible API changes
* **MINOR**: version when you add functionality in a backwards compatible manner
* **PATCH**: version when you make backwards compatible bug fixes

---

# Quick install

```console
# Windows
python -m pip install logyca
# Linux
pip install logyca
```

---

# Example of concepts using library APIResult

```python
# Example output from ApiResult:
result={
  "resultToken": {
    "token": "",
    "refreshToken": "",
    "result": "",
    "emailActiveDirectory": "",
    "message": ""
  },
  "resultObject": [
    {
      "name": "Database server",
      "status": 0,
      "description": "Connection status fine"
    },
    {
      "name": "Redis server",
      "status": 0,
      "description": "Connection status fine"
    }
  ],
  "apiException": {
    "message": "",
    "isError": false,
    "detail": null,
    "status": 200,
    "logycaStatus": 0
  },
  "resultMessage": "",
  "dataError": false
}
```

## Use cases: you must catch de exception

1. if you get data only the token:
```json
{
"dataError":false,
"resultObject":null,
"resultToken":"Not Null"
}
```

2. if you get data correctly
```json
{
"dataError":false,
"resultObject"="Not Null"
"resultToken"=null
}
```

3. if you don't get because the operation was cancelled
```json
{
"dataError":true,
"resultObject":null,
"resultToken":null,
"apiException.logycaStatus":1,
"apiException.status"=404,
"resultMessage":"exception messages: the operation was cancelled"
}
```
[optional]apiException.message="if needed, return an object with structured failure data other than exception messages"


# Example of using library APIResult + Health Check

```python

from logyca import HealthEnum, LogycaStatusEnum, APIResultDTO, ApiFilterExceptionDTO, HTTPExceptionDTO, HealthDTO, TokensDTO

tokensDTO=TokensDTO()
tokensDTO.token='Token Example'

apiFilterExceptionDTO=ApiFilterExceptionDTO()
apiFilterExceptionDTO.isError=False
apiFilterExceptionDTO.logycaStatus=LogycaStatusEnum.Already_Exists
apiFilterExceptionDTO.status=LogycaStatusEnum.Already_Exists.mappingHttpStatusCode

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

print(apiResultDTO.resultToken)
for item in apiResultDTO.resultObject:
    print(f'name={item.name},status={item.status},description={item.description}')
print(apiResultDTO.resultToken)

# output
# token='Token Example' refreshToken='' result='' emailActiveDirectory='' message=''
# name=Check CPU,status=0,description=OK
# name=Check Connect DB,status=1,description=Warning
# name=Check Connect Storage,status=2,description=Critical
# token='Token Example' refreshToken='' result='' emailActiveDirectory='' message=''
```

---

# Example of using helpers

```python
from logyca import buildUrl,convertDateTimeStampUTCtoUTCColombia

url1='https://domain.com'
url2='api/get'
print(f'buildUrl={buildUrl(url1,url2)}')
# ouput
# buildUrl=https://domain.com/api/get

datetimestampUTC=1679729109
print(f'datetimeUTCColombia={convertDateTimeStampUTCtoUTCColombia(datetimestampUTC)}')
# output
# datetimeUTCColombia=2023-03-25 02:25:09-05:00
```

---

# Current library test

```console
# Library installation

# Windows
python -m pip install logyca[test]
# Linux
pip install logyca

# Run it
pytest -s
```

---

# History

0.1.x
* The library is integrated into the first project.
* Start creating unit tests

0.0.x
* Deployment practicing.
