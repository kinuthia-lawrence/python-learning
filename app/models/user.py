from pydantic import BaseModel, EmailStr, field_validator

class User(BaseModel):
    name: str
    email: EmailStr
    account_id: int

    @field_validator('account_id') # Custom field validation
    def validate_account_id(cls, value):
        if value <= 0:
            raise ValueError('account_id must be a positive integer')
        return value



user_data = {
    "name": "John Doe",
    "email": "john@gmail.com",
    "account_id": 12345
}
# using a constructor
user = User(**user_data)
user2 = User(name="John Smith", email="johnsmith@gmail.com", account_id=67890)


user_json = user.model_dump_json()  # json serialization
user_dict = user.model_dump()   # dictionary serialization
user_from_json = User.model_validate_json(user_json)  # parse from json

print(user_json)
print(user)
print(user_dict)
print(user_from_json)



""" 
Dataclass  gives you type hints, doesn't support validation, serialization is limited but it's built into Python.
Pydantic provides validation, serialization, and more features out of the box but it's not built into Python. 
"""
from dataclasses import dataclass

@dataclass
class UserDataClass:
    name: str
    email: str
    account_id: int

user_dict = asdict(UserDataClass(name="Jane Doe", email="jane@gmail.com", account_id=54321)) # serialization to dictionary
