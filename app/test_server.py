import requests

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
