import requests
import time
import calendar

server = "http://127.0.0.1:8000";
print(requests.get(server).json())

print(requests.get(server + "/my-items").json())

create_new_user_response = requests.post(server + "/user",
                                         json={"username": "test", "password": "secret", "email": "mypublic@email.com",
                                               "full_name": "love programming"})
print(create_new_user_response.text)

print("status code: ",
      requests.post(server + "/items", json={"name": "example_name", "value": "idk", "price": 10.0}).status_code)
print("body: ", requests.post(server + "/items", json={"name": "example_name", "value": "idk", "price": 10.0}).text)

print(requests.get(server + "/wrestlers/fool").headers)

current_GMT = time.gmtime()
time_stamp = calendar.timegm(current_GMT)
print(requests.put(server + "/items-json-compatible/20", json={"title": "It's Valentine's Day", "timestamp": time_stamp}).text)


print(requests.get(server + "/protected/items", headers={"x-token": "fake-super-secret-token", "x-key": "fake-super-secret-key"}).text)
