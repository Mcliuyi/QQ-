import json
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen

from oauth.exceptions import QQAPIError
from . import constants

class OAuthQQ():
    """
    QQ第三方登录工具类
    保存QQ第三方登录需要的操作方法和数据
    """

    def __init__(self):
        """

        :rtype:
        """
        self.app_id = constants.QQ_APP_ID
        self.app_key = constants.QQ_APP_KEY
        self.redirect_uri = constants.QQ_REDIRECT_URI
        self.qq_url = constants.QQ_URL

    def generate_qq_login_url(self, state):
       """
       生成QQ登陆的url地址
       :param state: QQ登陆成功以后需要跳转的用户页面
       :return: QQ登陆地址
       """
       base_url = "https://graph.qq.com/oauth2.0/authorize" + "?"
       query_params = {
           "response_type": "code",  # 固定值
           "client_id": self.app_id,  # app id
           "redirect_uri": self.redirect_uri,
           "state": state,  # 登陆页面中的跳转地址
           "scope": "get_user_info",  # 声明使用的接口名称，可选
       }

       query_string = urlencode(query_params)

       url = base_url + query_string

       return url

    def get_qq_access_token(self,code):
        """凭借code发起请求到QQ服务器获取access_token"""
        # 拼接接口地址和参数
        base_url = "https://graph.qq.com/oauth2.0/token" + "?"
        query_params = {
            "grant_type": "authorization_code",
            "client_id": self.app_id,
            "client_secret": self.app_key,
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        # 把字典转换成查询字符串
        query_string = urlencode(query_params)
        url = base_url + query_string

        # 发起请求
        response = urlopen(url)
        # 读取数据
        # "access_token=30AD926372CC06EAB5B61AF32465F7F9&expires_in=7776000&refresh_token=1A79BA3A1B20D0AAE5E2BBEC042C1F30",
        response_data = response.read().decode()
        # 将数据转换为字典
        data = parse_qs(response_data)
        # {'access_token': ['76A8267B801001C1F6E7417B03F86C0F'], 'expires_in': ['7776000'], 'refresh_token': ['ED9954CD49D3B1CE0B01C5D3CD9AF233']}
        access_token = data.get('access_token')
        if not access_token:
           raise QQAPIError
        # # 返回access_token
        return access_token[0]

    def get_openid(self, access_token):
        """
        从QQ服务器获取用户openid
        :param access_token: qq提供的access_tokend
        :return:  open_id
        """
        url = self.qq_url + access_token
        response = urlopen(url)
        # 读取数据
        #  "token": "callback( {\"client_id\":\"101474184\",\"openid\":\"8908B7B73D115A13D23420609F17A9B3\"} );\n"
        response_data = response.read().decode()
        # 将数据转换为字典
        try:
            data = json.loads(response_data[10:-4])
        except:
            raise QQAPIError
        else:
            return data["openid"]


