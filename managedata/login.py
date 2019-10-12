#!/usr/bin/env python
# -*- coding: utf-8 -*-

def start(email):
    data = {
       "userInfoType":"EMAIL",
       "userInfo":"email",
       "attributesToReturn":[],
       "minRegistrationLevel":"BASIC"
    }

    data = base64.b64encode(json.dumps(data))
    result = requests.post('https://services.test.frejaeid.com/authentication/1.0/initAuthentication',data={"initAuthRequest":data}, verify=verify, cert=cert)
    authdata = base64.b64encode(result.content)
    laststatus = ""
    while 1:
      sleep(2)
      result2 = requests.post('https://services.test.frejaeid.com/authentication/1.0/getOneResult',data={"getOneAuthResultRequest":authdata}, verify=verify, cert=cert)
      thisstatus = result2.json()["status"]
      if not laststatus == thisstatus:
        laststatus = thisstatus
        print(thisstatus)
      if thisstatus in ("CANCELED","RP_CANCELED","EXPIRED","APPROVED","REJECTED"):
        break