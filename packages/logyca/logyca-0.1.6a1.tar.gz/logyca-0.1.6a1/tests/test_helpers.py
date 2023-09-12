from logyca import buildUrl

def test_helpers():
    '''Description
    Checking the helpers
    '''
    url1='https://domain.com'
    url2='api/get'
    assert buildUrl(url1,url2)=='https://domain.com/api/get'    

