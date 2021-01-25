from requests import session

masterSession = None

def get_session():
    global masterSession
    if masterSession:
        # print('session already initialized')
        return masterSession
    else:
        masterSession = session()
        return masterSession

