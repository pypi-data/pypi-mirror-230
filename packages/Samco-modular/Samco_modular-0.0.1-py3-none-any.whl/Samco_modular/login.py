from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge
import json

def samco_login(body):
    ###### SAMCO SWAPNA Login ########

    samco=StocknoteAPIPythonBridge()
    login=samco.login(body=body)
    login=json.loads(login)
    print(login)
    samco.set_session_token(sessionToken=login['sessionToken'])
    token=login['sessionToken']

    return [token,samco]
    ##this will return a user details and generated session token
