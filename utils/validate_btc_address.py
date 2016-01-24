# This program takes a Bitcoin address and validates if it is True of False

user_response = input("Enter the Bitcoin address you want to validate : ")
btc_address = user_response

from hashlib import sha256

digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
 
def decode_base58(btc_address, length):
    n = 0
    for char in btc_address:
        n = n * 58 + digits58.index(char)
    return n.to_bytes(length, 'big')

def check_btc(btc_address):
    btc_bytes = decode_base58(btc_address, 25)
    return btc_bytes[-4:] == sha256(sha256(btc_bytes[:-4]).digest()).digest()[:4]
 
# print("1", check_bc('1AGNa15ZQXAZUgFiqJ3i7Z2DPU2J6hW62i'))
# print("2", check_bc("17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j"))

print("Your Bitcoin address | ", btc_address, '| is ', check_btc(user_response))
