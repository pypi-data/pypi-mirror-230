# -*- coding: utf-8 -*-
# Module for PasscertService API. It include base functionality of the
# RESTful web service request and parse json result. It uses Linkhub module
# to accomplish authentication APIs.
#
# 
# Author : linkhub dev
# Written : 2023-03-08
# Updated : 2023-09-08
# Thanks for your interest.

from .base import BaseService, BarocertException

class PasscertService(BaseService):
    def __init__(self, LinkID, SecretKey, timeOut=15):
        """ 생성자.
            args
                LinkID : 링크허브에서 발급받은 LinkID
                SecretKey : 링크허브에서 발급받은 SecretKey
        """
        super(self.__class__, self).__init__(LinkID, SecretKey)
        self._addScope("441")
        self._addScope("442")
        self._addScope("443")
        self._addScope("444")

    # 본인인증 요청
    def requestIdentity(self, clientCode, identity):

        if clientCode == None or clientCode == "":
            raise BarocertException(-99999999, "이용기관코드가 입력되지 않았습니다.")
        if False == clientCode.isdigit():
            raise BarocertException(-99999999, "이용기관코드는 숫자만 입력할 수 있습니다.")
        if 12 != len(clientCode):
            raise BarocertException(-99999999, "이용기관코드는 12자 입니다.")
        if identity == None or identity == "":
            raise BarocertException(-99999999, "본인인증 요청정보가 입력되지 않았습니다.")    
        if identity.receiverHP == None or identity.receiverHP == "":
            raise BarocertException(-99999999, "수신자 휴대폰번호가 입력되지 않았습니다.")
        if identity.receiverName == None or identity.receiverName == "":
            raise BarocertException(-99999999, "수신자 성명이 입력되지 않았습니다.")
        if identity.reqTitle == None or identity.reqTitle == "":
            raise BarocertException(-99999999, "인증요청 메시지 제목이 입력되지 않았습니다.")
        if identity.callCenterNum == None or identity.callCenterNum == "":
            raise BarocertException(-99999999, "고객센터 연락처가 입력되지 않았습니다.")            
        if identity.expireIn == None or identity.expireIn == "":
            raise BarocertException(-99999999, "만료시간이 입력되지 않았습니다.")
        if identity.token == None or identity.token == "":
            raise BarocertException(-99999999, "토큰 원문이 입력되지 않았습니다.")
        
        postData = self._stringtify(identity)

        return self._httppost('/PASS/Identity/' + clientCode, postData)

    # 본인인증 상태확인
    def getIdentityStatus(self, clientCode, receiptId):

        if clientCode == None or clientCode == "":
            raise BarocertException(-99999999, "이용기관코드가 입력되지 않았습니다.")
        if False == clientCode.isdigit():
            raise BarocertException(-99999999, "이용기관코드는 숫자만 입력할 수 있습니다.")
        if 12 != len(clientCode):
            raise BarocertException(-99999999, "이용기관코드는 12자 입니다.")
        if receiptId == None or receiptId == "":
            raise BarocertException(-99999999, "접수아이디가 입력되지 않았습니다.")
        if False == receiptId.isdigit():
            raise BarocertException(-99999999, "접수아이디는 숫자만 입력할 수 있습니다.")
        if 32 != len(receiptId):
            raise BarocertException(-99999999, "접수아이디는 32자 입니다.")
        
        return self._httpget('/PASS/Identity/' + clientCode + '/' + receiptId )
    
    # 본인인증 검증
    def verifyIdentity(self, clientCode, receiptId, identityVerify):

        if clientCode == None or clientCode == "":
            raise BarocertException(-99999999, "이용기관코드가 입력되지 않았습니다.")
        if False == clientCode.isdigit():
            raise BarocertException(-99999999, "이용기관코드는 숫자만 입력할 수 있습니다.")
        if 12 != len(clientCode):
            raise BarocertException(-99999999, "이용기관코드는 12자 입니다.")
        if receiptId == None or receiptId == "":
            raise BarocertException(-99999999, "접수아이디가 입력되지 않았습니다.")
        if False == receiptId.isdigit():
            raise BarocertException(-99999999, "접수아이디는 숫자만 입력할 수 있습니다.")
        if 32 != len(receiptId):
            raise BarocertException(-99999999, "접수아이디는 32자 입니다.")
        if identityVerify == None or identityVerify == "":
            raise BarocertException(-99999999, "본인인증 검증 요청 정보가 입력되지 않았습니다.")
        if identityVerify.receiverHP == None or identityVerify.receiverHP == "":
            raise BarocertException(-99999999, "수신자 휴대폰번호가 입력되지 않았습니다.")
        if identityVerify.receiverName == None or identityVerify.receiverName == "":
            raise BarocertException(-99999999, "수신자 성명이 입력되지 않았습니다.")

        postData = self._stringtify(identityVerify)

        return self._httppost('/PASS/Identity/' + clientCode + '/' + receiptId, postData)

    # 전자서명 요청
    def requestSign(self, clientCode, sign):

        if clientCode == None or clientCode == "":
            raise BarocertException(-99999999, "이용기관코드가 입력되지 않았습니다.")
        if False == clientCode.isdigit():
            raise BarocertException(-99999999, "이용기관코드는 숫자만 입력할 수 있습니다.")
        if 12 != len(clientCode):
            raise BarocertException(-99999999, "이용기관코드는 12자 입니다.")
        if sign == None or sign == "":
            raise BarocertException(-99999999, "전자서명 요청정보가 입력되지 않았습니다.")
        if sign.receiverHP == None or sign.receiverHP == "":
            raise BarocertException(-99999999, "수신자 휴대폰번호가 입력되지 않았습니다.")
        if sign.receiverName == None or sign.receiverName == "":
            raise BarocertException(-99999999, "수신자 성명이 입력되지 않았습니다.")
        if sign.reqTitle == None or sign.reqTitle == "":
            raise BarocertException(-99999999, "인증요청 메시지 제목이 입력되지 않았습니다.")
        if sign.callCenterNum == None or sign.callCenterNum == "":
            raise BarocertException(-99999999, "고객센터 연락처가 입력되지 않았습니다.")            
        if sign.expireIn == None or sign.expireIn == "":
            raise BarocertException(-99999999, "만료시간이 입력되지 않았습니다.")
        if sign.token == None or sign.token == "":
            raise BarocertException(-99999999, "토큰 원문이 입력되지 않았습니다.")
        if sign.tokenType == None or sign.tokenType == "":
            raise BarocertException(-99999999, "원문 유형이 입력되지 않았습니다.")
        
        postData = self._stringtify(sign)

        return self._httppost('/PASS/Sign/' + clientCode, postData)

    # 전자서명 상태확인
    def getSignStatus(self, clientCode, receiptId):

        if clientCode == None or clientCode == "":
            raise BarocertException(-99999999, "이용기관코드가 입력되지 않았습니다.")
        if False == clientCode.isdigit():
            raise BarocertException(-99999999, "이용기관코드는 숫자만 입력할 수 있습니다.")
        if 12 != len(clientCode):
            raise BarocertException(-99999999, "이용기관코드는 12자 입니다.")
        if receiptId == None or receiptId == "":
            raise BarocertException(-99999999, "접수아이디가 입력되지 않았습니다.")
        if False == receiptId.isdigit():
            raise BarocertException(-99999999, "접수아이디는 숫자만 입력할 수 있습니다.")
        if 32 != len(receiptId):
            raise BarocertException(-99999999, "접수아이디는 32자 입니다.")

        return self._httpget('/PASS/Sign/' + clientCode + '/' + receiptId)

    # 전자서명 검증
    def verifySign(self, clientCode, receiptId, signVerify):

        if clientCode == None or clientCode == "":
            raise BarocertException(-99999999, "이용기관코드가 입력되지 않았습니다.")
        if False == clientCode.isdigit():
            raise BarocertException(-99999999, "이용기관코드는 숫자만 입력할 수 있습니다.")
        if 12 != len(clientCode):
            raise BarocertException(-99999999, "이용기관코드는 12자 입니다.")
        if receiptId == None or receiptId == "":
            raise BarocertException(-99999999, "접수아이디가 입력되지 않았습니다.")
        if False == receiptId.isdigit():
            raise BarocertException(-99999999, "접수아이디는 숫자만 입력할 수 있습니다.")
        if 32 != len(receiptId):
            raise BarocertException(-99999999, "접수아이디는 32자 입니다.")
        if signVerify == None or signVerify == "":
            raise BarocertException(-99999999, "전자서명 검증 요청 정보가 입력되지 않았습니다.")
        if signVerify.receiverHP == None or signVerify.receiverHP == "":
            raise BarocertException(-99999999, "수신자 휴대폰번호가 입력되지 않았습니다.")
        if signVerify.receiverName == None or signVerify.receiverName == "":
            raise BarocertException(-99999999, "수신자 성명이 입력되지 않았습니다.")        

        postData = self._stringtify(signVerify)    

        return self._httppost('/PASS/Sign/' + clientCode + '/' + receiptId, postData)
    
    # 출금동의 요청
    def requestCMS(self, clientCode, cms):
        
        if clientCode == None or clientCode == "":
            raise BarocertException(-99999999, "이용기관코드가 입력되지 않았습니다.")
        if False == clientCode.isdigit():
            raise BarocertException(-99999999, "이용기관코드는 숫자만 입력할 수 있습니다.")
        if 12 != len(clientCode):
            raise BarocertException(-99999999, "이용기관코드는 12자 입니다.")
        if cms == None or cms == "":
            raise BarocertException(-99999999, "자동이체 출금동의 요청정보가 입력되지 않았습니다.")
        if cms.receiverHP == None or cms.receiverHP == "":
            raise BarocertException(-99999999, "수신자 휴대폰번호가 입력되지 않았습니다.")
        if cms.receiverName == None or cms.receiverName == "":
            raise BarocertException(-99999999, "수신자 성명이 입력되지 않았습니다.")
        if cms.reqTitle == None or cms.reqTitle == "":
            raise BarocertException(-99999999, "인증요청 메시지 제목이 입력되지 않았습니다.")
        if cms.callCenterNum == None or cms.callCenterNum == "":
            raise BarocertException(-99999999, "고객센터 연락처가 입력되지 않았습니다.")              
        if cms.expireIn == None or cms.expireIn == "":
            raise BarocertException(-99999999, "만료시간이 입력되지 않았습니다.")
        if cms.bankName == None or cms.bankName == "":
            raise BarocertException(-99999999, "출금은행명이 입력되지 않았습니다.")
        if cms.bankAccountNum == None or cms.bankAccountNum == "":
            raise BarocertException(-99999999, "출금계좌번호가 입력되지 않았습니다.")
        if cms.bankAccountName == None or cms.bankAccountName == "":
            raise BarocertException(-99999999, "출금계좌 예금주명이 입력되지 않았습니다.")
        if cms.bankServiceType == None or cms.bankServiceType == "":
            raise BarocertException(-99999999, "출금 유형이 입력되지 않았습니다.")

        postData = self._stringtify(cms)

        return self._httppost('/PASS/CMS/' + clientCode, postData)

    # 출금동의 상태확인
    def getCMSStatus(self, clientCode, receiptId):

        if clientCode == None or clientCode == "":
            raise BarocertException(-99999999, "이용기관코드가 입력되지 않았습니다.")
        if False == clientCode.isdigit():
            raise BarocertException(-99999999, "이용기관코드는 숫자만 입력할 수 있습니다.")
        if 12 != len(clientCode):
            raise BarocertException(-99999999, "이용기관코드는 12자 입니다.")
        if receiptId == None or receiptId == "":
            raise BarocertException(-99999999, "접수아이디가 입력되지 않았습니다.")
        if False == receiptId.isdigit():
            raise BarocertException(-99999999, "접수아이디는 숫자만 입력할 수 있습니다.")
        if 32 != len(receiptId):
            raise BarocertException(-99999999, "접수아이디는 32자 입니다.")

        return self._httpget('/PASS/CMS/' + clientCode + '/' + receiptId)

    # 출금동의 검증
    def verifyCMS(self, clientCode, receiptId, cmsVerify):

        if clientCode == None or clientCode == "":
            raise BarocertException(-99999999, "이용기관코드가 입력되지 않았습니다.")
        if False == clientCode.isdigit():
            raise BarocertException(-99999999, "이용기관코드는 숫자만 입력할 수 있습니다.")
        if 12 != len(clientCode):
            raise BarocertException(-99999999, "이용기관코드는 12자 입니다.")
        if receiptId == None or receiptId == "":
            raise BarocertException(-99999999, "접수아이디가 입력되지 않았습니다.")
        if False == receiptId.isdigit():
            raise BarocertException(-99999999, "접수아이디는 숫자만 입력할 수 있습니다.")
        if 32 != len(receiptId):
            raise BarocertException(-99999999, "접수아이디는 32자 입니다.")
        if cmsVerify == None or cmsVerify == "":
            raise BarocertException(-99999999, "자동이체 출금동의 검증 요청 정보가 입력되지 않았습니다.")
        if cmsVerify.receiverHP == None or cmsVerify.receiverHP == "":
            raise BarocertException(-99999999, "수신자 휴대폰번호가 입력되지 않았습니다.")
        if cmsVerify.receiverName == None or cmsVerify.receiverName == "":
            raise BarocertException(-99999999, "수신자 성명이 입력되지 않았습니다.")                
        
        postData = self._stringtify(cmsVerify)

        return self._httppost('/PASS/CMS/' + clientCode + '/' + receiptId, postData)
    
    # 간편로그인 요청
    def requestLogin(self, clientCode, login):

        if clientCode == None or clientCode == "":
            raise BarocertException(-99999999, "이용기관코드가 입력되지 않았습니다.")
        if False == clientCode.isdigit():
            raise BarocertException(-99999999, "이용기관코드는 숫자만 입력할 수 있습니다.")
        if 12 != len(clientCode):
            raise BarocertException(-99999999, "이용기관코드는 12자 입니다.")
        if login == None or login == "":
            raise BarocertException(-99999999, "간편로그인 요청정보가 입력되지 않았습니다.")    
        if login.receiverHP == None or login.receiverHP == "":
            raise BarocertException(-99999999, "수신자 휴대폰번호가 입력되지 않았습니다.")
        if login.receiverName == None or login.receiverName == "":
            raise BarocertException(-99999999, "수신자 성명이 입력되지 않았습니다.")
        if login.reqTitle == None or login.reqTitle == "":
            raise BarocertException(-99999999, "인증요청 메시지 제목이 입력되지 않았습니다.")
        if login.callCenterNum == None or login.callCenterNum == "":
            raise BarocertException(-99999999, "고객센터 연락처가 입력되지 않았습니다.")            
        if login.expireIn == None or login.expireIn == "":
            raise BarocertException(-99999999, "만료시간이 입력되지 않았습니다.")
        if login.token == None or login.token == "":
            raise BarocertException(-99999999, "토큰 원문이 입력되지 않았습니다.")
        
        postData = self._stringtify(login)

        return self._httppost('/PASS/Login/' + clientCode, postData)

    # 간편로그인 상태확인
    def getLoginStatus(self, clientCode, receiptId):

        if clientCode == None or clientCode == "":
            raise BarocertException(-99999999, "이용기관코드가 입력되지 않았습니다.")
        if False == clientCode.isdigit():
            raise BarocertException(-99999999, "이용기관코드는 숫자만 입력할 수 있습니다.")
        if 12 != len(clientCode):
            raise BarocertException(-99999999, "이용기관코드는 12자 입니다.")
        if receiptId == None or receiptId == "":
            raise BarocertException(-99999999, "접수아이디가 입력되지 않았습니다.")
        if False == receiptId.isdigit():
            raise BarocertException(-99999999, "접수아이디는 숫자만 입력할 수 있습니다.")
        if 32 != len(receiptId):
            raise BarocertException(-99999999, "접수아이디는 32자 입니다.")
        
        return self._httpget('/PASS/Login/' + clientCode + '/' + receiptId )
    
    # 간편로그인 검증
    def verifyLogin(self, clientCode, receiptId, loginVerify):

        if clientCode == None or clientCode == "":
            raise BarocertException(-99999999, "이용기관코드가 입력되지 않았습니다.")
        if False == clientCode.isdigit():
            raise BarocertException(-99999999, "이용기관코드는 숫자만 입력할 수 있습니다.")
        if 12 != len(clientCode):
            raise BarocertException(-99999999, "이용기관코드는 12자 입니다.")
        if receiptId == None or receiptId == "":
            raise BarocertException(-99999999, "접수아이디가 입력되지 않았습니다.")
        if False == receiptId.isdigit():
            raise BarocertException(-99999999, "접수아이디는 숫자만 입력할 수 있습니다.")
        if 32 != len(receiptId):
            raise BarocertException(-99999999, "접수아이디는 32자 입니다.")
        if loginVerify == None or loginVerify == "":
            raise BarocertException(-99999999, "본인인증 검증 요청 정보가 입력되지 않았습니다.")
        if loginVerify.receiverHP == None or loginVerify.receiverHP == "":
            raise BarocertException(-99999999, "수신자 휴대폰번호가 입력되지 않았습니다.")
        if loginVerify.receiverName == None or loginVerify.receiverName == "":
            raise BarocertException(-99999999, "수신자 성명이 입력되지 않았습니다.")

        postData = self._stringtify(loginVerify)

        return self._httppost('/PASS/Login/' + clientCode + '/' + receiptId, postData)

class PassCMS(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

class PassIdentity(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        
class PassLogin(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs        

class PassSign(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

class PassCMS(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

class PassIdentity(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        
class PassLoginVerify(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs        

class PassSignVerify(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

class PassCMSVerify(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

class PassIdentityVerify(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        