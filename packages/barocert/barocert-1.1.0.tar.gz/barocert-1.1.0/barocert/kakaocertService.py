# -*- coding: utf-8 -*-
# Module for KakaocertService API. It include base functionality of the
# RESTful web service request and parse json result. It uses Linkhub module
# to accomplish authentication APIs.
#
# 
# Author : linkhub dev
# Written : 2023-03-08
# Updated : 2023-09-08
# Thanks for your interest.

from .base import BaseService, BarocertException

class KakaocertService(BaseService):
    def __init__(self, LinkID, SecretKey, timeOut=15):
        """ 생성자.
            args
                LinkID : 링크허브에서 발급받은 LinkID
                SecretKey : 링크허브에서 발급받은 SecretKey
        """
        super(self.__class__, self).__init__(LinkID, SecretKey)
        self._addScope("401")
        self._addScope("402")
        self._addScope("403")
        self._addScope("404")
        self._addScope("405")
    
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
        if identity.receiverBirthday == None or identity.receiverBirthday == "":
            raise BarocertException(-99999999, "생년월일이 입력되지 않았습니다.")
        if identity.reqTitle == None or identity.reqTitle == "":
            raise BarocertException(-99999999, "인증요청 메시지 제목이 입력되지 않았습니다.")
        if identity.expireIn == None or identity.expireIn == "":
            raise BarocertException(-99999999, "만료시간이 입력되지 않았습니다.")
        if identity.token == None or identity.token == "":
            raise BarocertException(-99999999, "토큰 원문이 입력되지 않았습니다.")
        
        postData = self._stringtify(identity)

        return self._httppost('/KAKAO/Identity/' + clientCode, postData)

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
        

        return self._httpget('/KAKAO/Identity/' + clientCode + '/' + receiptId )
    
    # 본인인증 검증
    def verifyIdentity(self, clientCode, receiptId):

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

        return self._httppost('/KAKAO/Identity/' + clientCode + '/' + receiptId )

    # 전자서명 요청(단건)
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
        if sign.receiverBirthday == None or sign.receiverBirthday == "":
            raise BarocertException(-99999999, "생년월일이 입력되지 않았습니다.")
        if sign.reqTitle == None or sign.reqTitle == "":
            raise BarocertException(-99999999, "인증요청 메시지 제목이 입력되지 않았습니다.")
        if sign.expireIn == None or sign.expireIn == "":
            raise BarocertException(-99999999, "만료시간이 입력되지 않았습니다.")
        if sign.token == None or sign.token == "":
            raise BarocertException(-99999999, "토큰 원문이 입력되지 않았습니다.")
        if sign.tokenType == None or sign.tokenType == "":
            raise BarocertException(-99999999, "원문 유형이 입력되지 않았습니다.")
        
        postData = self._stringtify(sign)

        return self._httppost('/KAKAO/Sign/' + clientCode, postData)

    # 전자서명 상태확인(단건)
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

        return self._httpget('/KAKAO/Sign/' + clientCode + '/' + receiptId)

    # 전자서명 검증(단건)
    def verifySign(self, clientCode, receiptId):

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

        return self._httppost('/KAKAO/Sign/' + clientCode + '/' + receiptId)
    
    # 전자서명 요청(복수)
    def requestMultiSign(self, clientCode, multiSign):

        if clientCode == None or clientCode == "":
            raise BarocertException(-99999999, "이용기관코드가 입력되지 않았습니다.")
        if False == clientCode.isdigit():
            raise BarocertException(-99999999, "이용기관코드는 숫자만 입력할 수 있습니다.")
        if 12 != len(clientCode):
            raise BarocertException(-99999999, "이용기관코드는 12자 입니다.")
        if multiSign == None or multiSign == "":
            raise BarocertException(-99999999, "전자서명 요청정보가 입력되지 않았습니다.")
        if multiSign.receiverHP == None or multiSign.receiverHP == "":
            raise BarocertException(-99999999, "수신자 휴대폰번호가 입력되지 않았습니다.")
        if multiSign.receiverName == None or multiSign.receiverName == "":
            raise BarocertException(-99999999, "수신자 성명이 입력되지 않았습니다.")
        if multiSign.receiverBirthday == None or multiSign.receiverBirthday == "":
            raise BarocertException(-99999999, "생년월일이 입력되지 않았습니다.")
        if multiSign.reqTitle == None or multiSign.reqTitle == "":
            raise BarocertException(-99999999, "인증요청 메시지 제목이 입력되지 않았습니다.")
        if multiSign.expireIn == None or multiSign.expireIn == "":
            raise BarocertException(-99999999, "만료시간이 입력되지 않았습니다.")
        if self._isNullorEmptyTitle(multiSign.tokens):
            raise BarocertException(-99999999, "인증요청 메시지 제목이 입력되지 않았습니다.")
        if self._isNullorEmptyToken(multiSign.tokens):
            raise BarocertException(-99999999, "토큰 원문이 입력되지 않았습니다.")
        if multiSign.tokenType == None or multiSign.tokenType == "":
            raise BarocertException(-99999999, "원문 유형이 입력되지 않았습니다.")

        postData = self._stringtify(multiSign)

        return self._httppost('/KAKAO/MultiSign/' + clientCode, postData)

    # 전자서명 상태확인(복수)	
    def getMultiSignStatus(self, clientCode, receiptId):

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

        return self._httpget('/KAKAO/MultiSign/' + clientCode + '/' + receiptId)


    # 전자서명 검증(복수)
    def verifyMultiSign(self, clientCode, receiptId):

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
        
        return self._httppost('/KAKAO/MultiSign/' + clientCode + '/' + receiptId)

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
        if cms.receiverBirthday == None or cms.receiverBirthday == "":
            raise BarocertException(-99999999, "생년월일이 입력되지 않았습니다.")
        if cms.reqTitle == None or cms.reqTitle == "":
            raise BarocertException(-99999999, "인증요청 메시지 제목이 입력되지 않았습니다.")
        if cms.expireIn == None or cms.expireIn == "":
            raise BarocertException(-99999999, "만료시간이 입력되지 않았습니다.")
        if cms.requestCorp == None or cms.requestCorp == "":
            raise BarocertException(-99999999, "청구기관명이 입력되지 않았습니다.")
        if cms.bankName == None or cms.bankName == "":
            raise BarocertException(-99999999, "은행명이 입력되지 않았습니다.")
        if cms.bankAccountNum == None or cms.bankAccountNum == "":
            raise BarocertException(-99999999, "계좌번호가 입력되지 않았습니다.")
        if cms.bankAccountName == None or cms.bankAccountName == "":
            raise BarocertException(-99999999, "예금주명이 입력되지 않았습니다.")
        if cms.bankAccountBirthday == None or cms.bankAccountBirthday == "":
            raise BarocertException(-99999999, "예금주 생년월일이 입력되지 않았습니다.")
        if cms.bankServiceType == None or cms.bankServiceType == "":
            raise BarocertException(-99999999, "출금 유형이 입력되지 않았습니다.")

        postData = self._stringtify(cms)

        return self._httppost('/KAKAO/CMS/' + clientCode, postData)

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

        return self._httpget('/KAKAO/CMS/' + clientCode + '/' + receiptId)

    # 출금동의 검증
    def verifyCMS(self, clientCode, receiptId):

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
        
        return self._httppost('/KAKAO/CMS/' + clientCode + '/' + receiptId)
    
    # 간편로그인 검증
    def verifyLogin(self, clientCode, txID):

        if clientCode == None or clientCode == "":
            raise BarocertException(-99999999, "이용기관코드가 입력되지 않았습니다.")
        if False == clientCode.isdigit():
            raise BarocertException(-99999999, "이용기관코드는 숫자만 입력할 수 있습니다.")
        if 12 != len(clientCode):
            raise BarocertException(-99999999, "이용기관코드는 12자 입니다.")
        if txID == None or txID == "":
            raise BarocertException(-99999999, "트랜잭션 아이디가 입력되지 않았습니다.")
        
        return self._httppost('/KAKAO/Login/' + clientCode + '/' + txID)

    def _isNullorEmptyTitle(self, multiSignTokens):
        if multiSignTokens == None or multiSignTokens == "":
            return True
        if len(multiSignTokens) == 0:
            return True
        for multiSignToken in multiSignTokens:
            if multiSignToken.reqTitle == None or multiSignToken.reqTitle == "":
                return True
        return False
    
    def _isNullorEmptyToken(self, multiSignTokens):
        if multiSignTokens == None or multiSignTokens == "":
            return True
        if len(multiSignTokens) == 0:
            return True
        for multiSignToken in multiSignTokens:
            if multiSignToken.token == None or multiSignToken.token == "":
                return True
        return False


class KakaoCMS(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

class KakaoIdentity(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        
class KakaoSign(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

class KakaoMultiSign(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

class KakaoMultiSignTokens(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs
