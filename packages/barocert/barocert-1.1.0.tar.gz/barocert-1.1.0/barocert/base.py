# -*- coding: utf-8 -*-
# Module for barocertService API. It include base functionality of the
# RESTful web service request and parse json result. It uses Linkhub module
# to accomplish authentication APIs.
#
# 
# Author : linkhub dev
# Written : 2023-03-08
# Updated : 2023-09-08
# Thanks for your interest.

import json
import zlib
import base64
import hmac
import json

from io import BytesIO
from hashlib import sha256
from time import time as stime
from json import JSONEncoder
from collections import namedtuple
from Crypto.Util import Counter
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

try:
    import http.client as httpclient
except ImportError:
    import httplib as httpclient

import linkhub

from linkhub import LinkhubException

ServiceID = 'BAROCERT'
ServiceURL = 'barocert.linkhub.co.kr'
ServiceURL_Static = 'static-barocert.linkhub.co.kr'
APIVERSION = '2.1'

def __with_metaclass(meta, *bases):
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)

    return type.__new__(metaclass, 'temporary_class', (), {})

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class BaseService(__with_metaclass(Singleton, object)):
    IPRestrictOnOff = False
    UseStaticIP = True
    UseLocalTimeYN = False
    _ServiceURL = ''

    def __init__(self, LinkID, SecretKey, timeOut=15):
        """ 생성자.
            args
                LinkID : 링크허브에서 발급받은 LinkID
                SecretKey : 링크허브에서 발급받은 SecretKey
        """
        self.__linkID = LinkID
        self.__secretKey = SecretKey
        self.__scopes = ["partner"]
        self.__tokenCache = {}
        self.__conn = None
        self.__connectedAt = stime()
        self.__timeOut = timeOut

    def ServiceURL(self, ServiceURL):
        self._ServiceURL = ServiceURL
        
    def AuthURL(self, AuthURL):
        linkhub.authURL(AuthURL)
        
    def _getConn(self):
        if self._ServiceURL != None and self._ServiceURL != '':
            if 'https://' in self._ServiceURL :
                url = self._ServiceURL.replace('https://', '').split(':')
                host = url[0]
                if len(url) == 1 :
                    self.__conn = httpclient.HTTPSConnection(host)
                elif len(url) > 1 :
                    port = url[1]
                    self.__conn = httpclient.HTTPSConnection(host + ":" + port)
            elif 'http://' in self._ServiceURL :
                url = self._ServiceURL.replace('http://', '').split(':')
                host = url[0]
                if len(url) == 1 :
                    self.__conn = httpclient.HTTPConnection(host)
                elif len(url) > 1 :
                    port = url[1]
                    self.__conn = httpclient.HTTPConnection(host + ":" + port)
            else :
                raise BarocertException(-99999999, 'ServiceURL에 전송 프로토콜(HTTP 또는 HTTPS)을 포함하여 주시기 바랍니다.')
            self.__connectedAt = stime()
            return self.__conn

        if stime() - self.__connectedAt >= self.__timeOut or self.__conn == None:
            if self.UseStaticIP :
                self.__conn = httpclient.HTTPSConnection(ServiceURL_Static)
            else :
                self.__conn = httpclient.HTTPSConnection(ServiceURL)

            self.__connectedAt = stime()
            return self.__conn
        else:
            return self.__conn

    def _addScope(self, newScope):
        self.__scopes.append(newScope)

    def _getToken(self):

        try:
            token = self.__tokenCache[self.__linkID]
        except KeyError:
            token = None

        refreshToken = True

        if token != None:
            refreshToken = token.expiration[:-5] < linkhub.getTime(self.UseStaticIP, self.UseLocalTimeYN, False)

        if refreshToken:
            try:
                token = linkhub.generateToken(self.__linkID, self.__secretKey,
                                              ServiceID, "", self.__scopes, None if self.IPRestrictOnOff else "*",
                                              self.UseStaticIP, self.UseLocalTimeYN, False)

                try:
                    del self.__tokenCache[self.__linkID]
                except KeyError:
                    pass

                self.__tokenCache[self.__linkID] = token

            except LinkhubException as LE:
                raise BarocertException(LE.code, LE.message)

        return token

    def _httpget(self, url):

        conn = self._getConn()

        headers = {"x-pb-version": APIVERSION}

        headers["Authorization"] = "Bearer " + self._getToken().session_token

        headers["Accept-Encoding"] = "gzip,deflate"

        conn.request('GET', url, '', headers)

        response = conn.getresponse()
        responseString = response.read()

        if Utils.isGzip(response, responseString):
            responseString = Utils.gzipDecomp(responseString)

        if response.status != 200:
            err = Utils.json2obj(responseString)
            raise BarocertException(int(err.code), err.message)
        else:
            return Utils.json2obj(responseString)

    def _httppost(self, url, postData = None):

        xDate = linkhub.getTime(self.UseStaticIP, False, False)

        signTarget = ""
        signTarget += "POST\n"
        if postData != None and postData != "":
            signTarget += Utils.b64_sha256(postData) + "\n"
        
        signTarget += xDate + "\n"
        signTarget += url +"\n"

        signature = Utils.b64_hmac_sha256(self.__secretKey, signTarget)

        conn = self._getConn()

        headers = {"x-bc-date": xDate}
        headers["x-bc-version"] = APIVERSION
        headers["Authorization"] = "Bearer " + self._getToken().session_token
        headers["Content-Type"] = "application/json; charset=utf8"
        headers["Accept-Encoding"] = "gzip,deflate"
        headers["x-bc-auth"] = signature
        headers["x-bc-encryptionmode"] = "GCM"

        conn.request('POST', url, postData, headers)

        response = conn.getresponse()
        responseString = response.read()

        if Utils.isGzip(response, responseString):
            responseString = Utils.gzipDecomp(responseString)

        if response.status != 200:
            err = Utils.json2obj(responseString)
            raise BarocertException(int(err.code), err.message)
        else:
            return Utils.json2obj(responseString)

    def _parse(self, jsonString):
        return Utils.json2obj(jsonString)

    def _stringtify(self, obj):
        return json.dumps(obj, cls=BarocertEncoder)
    
    def _encrypt(self, plainText):
        return Utils.AES256GCM(plainText, self.__secretKey)

class BarocertEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

class JsonObject(object):
    def __init__(self, dic):
        try:
            d = dic.__dict__
        except AttributeError:
            d = dic._asdict()

        self.__dict__.update(d)

    def __getattr__(self, name):
        return None

class Utils:
    @staticmethod
    def b64_sha256(input):
        return base64.b64encode(sha256(input.encode('utf-8')).digest()).decode('utf-8')

    @staticmethod
    def b64_hmac_sha256(keyString, targetString):
        return base64.b64encode(hmac.new(base64.b64decode(keyString.encode('utf-8')), targetString.encode('utf-8'), sha256).digest()).decode('utf-8').rstrip('\n')

    @staticmethod
    def _json_object_hook(d):
        return JsonObject(namedtuple('JsonObject', d.keys())(*d.values()))

    @staticmethod
    def json2obj(data):
        if (type(data) is bytes): data = data.decode('utf-8')
        return json.loads(data, object_hook=Utils._json_object_hook)

    @staticmethod
    def isGzip(response, data):
        if (response.getheader('Content-Encoding') != None and
                'gzip' in response.getheader('Content-Encoding')):
            return True
        else:
            return False

    @staticmethod
    def gzipDecomp(data):
        return zlib.decompress(data, 16 + zlib.MAX_WBITS)

    @staticmethod
    def AES256GCM(plainText, secretKey):
        iv = get_random_bytes(12)
        cipher = AES.new(base64.b64decode(secretKey), AES.MODE_GCM, iv)
        enc, tag = cipher.encrypt_and_digest(plainText.encode('utf-8'))
        return base64.b64encode(iv + enc + tag ).decode('utf-8')        

class BarocertException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
