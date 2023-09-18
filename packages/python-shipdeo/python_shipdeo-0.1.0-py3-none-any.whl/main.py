from shipdeo.auth import ShipdeoAuth
from shipdeo.shipping import ShipdeoService

if __name__ == '__main__':
    # auth = ShipdeoAuth(client_id='UTPPQaIaky08uk0f',client_secret='44lFd1Hkcudfil0h',is_prod=False)
    # token = auth.get_token()
    # print("TOken ", token)
    token = '8996777f8ea5f3e12caeddd415a11b48ccac13f3'
    shipdeo = ShipdeoService(token,is_prod=False)
    params = {'take': 2, 'skip': 0}
    respond = shipdeo.get_orders(params)
    print(respond)