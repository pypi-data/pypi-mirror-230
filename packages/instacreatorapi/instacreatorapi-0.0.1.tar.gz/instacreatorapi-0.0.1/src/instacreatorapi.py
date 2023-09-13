import requests

headers={
    "Content-Type": "application/json",
}


apikey='gamer'
def send_sms(number,proxy,apikey):
    num=str(number).replace('+','')
    apikey=str(apikey)
    if "https://" in proxy:
        proxy = proxy.replace("https://", "")
    if "http://" in proxy:
        proxy = proxy.replace("http://", "")
    if "http" in proxy:
        proxy = proxy.replace("http", "")
    if "https" in proxy:
        proxy = proxy.replace("https", "")

    proc=str(proxy)

    data = {
        "api-key": apikey,
        "number": num,
        "proxy": proc
    }

    r = requests.post("http://128.140.99.16:6969/api/send-sms", json=data, headers=headers, timeout=100)
    return r.json()

def create_acc(securetoken,proxy,otp,apikey):
    securetoken=str(securetoken)
    otp=str(otp)
    apikey=str(apikey)
    if "https://" in proxy:
        proxy = proxy.replace("https://", "")
    if "http://" in proxy:
        proxy = proxy.replace("http://", "")
    if "http" in proxy:
        proxy = proxy.replace("http", "")
    if "https" in proxy:
        proxy = proxy.replace("https", "")
    proc=str(proxy)
    data = {
        "api-key": apikey,
        "securetoken": securetoken,
        "proxy": proc,
        "otp": otp
    }
    r = requests.post("http://128.140.99.16:6969/api/create-acc", json=data, headers=headers, timeout=100)
    return r.json()

