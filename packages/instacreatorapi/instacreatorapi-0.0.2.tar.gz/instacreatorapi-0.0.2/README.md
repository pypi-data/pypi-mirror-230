# Instagram Account Creator Api

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)                 
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)   

[Contact me @god_x_gamer](https://telegram.me/@god_x_gamer)


## pip install instacreatorapi

## Functionality of the Api

- Can Create Account Without Blocked By Instagram
- Multi-Threading Supported
- Proxy Supported
- Automatically Generate Human Like Username
- Can Create Account In 2 simple step
- Detect suspended Accounts Also

## Usage

- Make sure you have Python installed in your system.
- Run Following command in the CMD.
 ```
  pip install instacreatorapi
  ```
## Example

 ```
# test.py
from instacreatorapi import send_sms,create_acc

proc = "username:password@host:port"  
num = "91xxxxxxxxxx"
apikey='xxxxxx'  #" free key - gamer "
send=send_sms(number=num,proxy=proc,apikey=apikey)
if "securetoken" in send:
    securetoken=r['message']['securetoken']
else:
    print(send)
    
otp='xxxx' # your otp 
create=create_acc(securetoken=securetoken,apikey=apikey,proxy=proc,otp=otp#)
print(create)
  ```

## Run the following Script.
 ```
  python test.py
 ```


## Note 
- I have tried to implement all the functionality, it might have some bugs also.
- Report Bugs [@god_x_gamer (telegram)](https://telegram.me/@god_x_gamer)

## If You Have Any Problems Or Want To Try My Api Contact Me On Telegram
- [Telegram Channel @gxtools](https://telegram.me/@gxtools)
- [Contact me @god_x_gamer](https://telegram.me/@god_x_gamer)



