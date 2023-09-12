from urllib import parse

def buildUrl(url1:str,url2:str)->str:
    '''Description    
    Build a from url correctly
    :param url1: http(s)://initial/string
    :param url2: following url path
    :return str: url
    '''
    return parse.urljoin(url1, url2)