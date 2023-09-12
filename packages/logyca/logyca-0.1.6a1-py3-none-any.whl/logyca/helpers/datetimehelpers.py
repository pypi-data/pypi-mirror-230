from datetime import datetime
import pytz
from logyca.common.constants import Constants

def convertDateTimeStampUTCtoUTCColombia(timestamp)->datetime:
    '''Description    
    Build a from url correctly
    :param timestamp:int: timestamp as timezone UTC
    :return datetime: datetime as timezone UTC(-5) Colombia
    '''
    expUTC=datetime.utcfromtimestamp(timestamp)
    timezoneUTC = pytz.timezone(Constants.TimeZoneUTC)
    dateTimeUTC = timezoneUTC.localize(expUTC, is_dst=None)
    dateTimeColombia = dateTimeUTC.astimezone(pytz.timezone(Constants.TimeZoneColombia))
    return dateTimeColombia