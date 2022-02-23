# import requests

# url = "https://api.paystack.co/bank?country=nigeria&perPage=100"

# payload={}
# headers = {}

# response = requests.request("GET", url, headers=headers, data=payload)

# print(response.text)

# import requests

# url = "https://api.flutterwave.com/v3/banks/NG"

# headers = {
#     "Accept": "application/json",
#     "Authorization": "Bearer FLWSECK_TEST-SANDBOXDEMOKEY-X"
# }

# response = requests.request("GET", url, headers=headers)

# print(response.text)

count = 0
sum = 0

while count <= 5:
    sum = sum + count * (count - 1)
    count = count + 1

print(sum)