from logyca.data.enums.healthenum import HealthEnum

class HealthDTO():
    '''Description
    LOGYCA HTTP Custom States
    :param name:str Gets or sets health status name
    :param status:HealthEnum Gets or sets health check status response code
    :param description:str Gets or sets description of the monitoring process
    :return int: Integer according to variable meaning
    '''
    name:str
    status:HealthEnum
    description:str
    def __init__(self, name='', status=HealthEnum.Ok,description=''):
        self.name = name
        self.status = status
        self.description = description