from enum import IntEnum

class HealthEnum(IntEnum):
        '''Description
        Health check status result
        :param OK: The method was able to check the service and it appeared to be functioning properly
        :param Warning: The method was able to check the service but it appeared to be above some "warning" threshold or did not appear to be working properly
        :param Critical: The method detected that either the service was not running or it was above some "critical" threshold
        :param Unknown: The method cannot answer a valid test
        :return int: Integer according to variable meaning
        '''
        Ok = 0
        Warning = 1
        Critical = 2
        Unknown = 3
