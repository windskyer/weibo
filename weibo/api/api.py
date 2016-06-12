import os
import webbrowser
try:
    import cPickle as pkl
except:
    import pickle as pkl


from weibo.common import cfg
from weibo.api.client import Client


CONF = cfg.CONF

class useAPI(object):
    def __init__(self, conf):
        self.app_key = conf.app_key
        self.app_secret = conf.app_secret
        self.callback_url = conf.callback_url
        self.token_file = conf.token_file

        self.token_file = os.path.join(os.path.dirname(__file__), self.token_file).replace('\\', '/')
        self.checked = self.check()

    def check(self):
        if os.path.isfile(self.token_file):
            try:
                token = pkl.load(open(self.token_file, 'r'))
                api = Client(self.app_key, self.app_secret, self.callback_url, token)
                try:
                    api.get('statuses/user_timeline')
                    self.api = api
                    return True
                except:
                    print("token maybe out of time!")
            except:
                print("The token file error")
        return False

    def token(self, CODE=''):
        client, url = self.getCODE()
        if self.checked == False:
            if CODE == '':
                webbrowser.open_new(url)
                try:
                    # for python2.x
                    CODE = raw_input("Please Input the Code: ").strip()
                except:
                    # for python3.x
                    CODE = input("Please Input the Code: ").strip()
            try:
                client.set_code(CODE)
            except:
                print("Maybe wrong CODE")
                return
        token = client.token
        pkl.dump(token, open(str(self.token_file), 'wb'))
        self.api = Client(self.app_key, self.app_secret, self.callback_url, token)
        self.checked = True

    def getCODE(self):
        client = Client(self.app_key, self.app_secret, self.callback_url)
        return client, client.authorize_url

    def getURL(self):
        client = Client(self.app_key, self.app_secret, self.callback_url)
        return client.authorize_url

    def get(self, url, count=200, **kwargs):
        kwargs['count'] = count
        if self.checked == False:
            self.token()
        return self.api.get(url, **kwargs)

    def post(self, url, **kwargs):
        if self.checked == False:
            self.token()
        return self.api.post(url, **kwargs)
