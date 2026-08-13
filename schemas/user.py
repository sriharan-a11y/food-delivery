from pydantic import BaseModel,EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email:EmailStr
    password:str
    full_name:str
    phone_number:Optional[str]=None
    role:str="customer"

class UserUpdate(BaseModel):
   # email:EmailStr |None=None
    full_name:Optional[str]=None
    phone_number:Optional[str]=None
    #password:str |None=None
    role:Optional[str]=None
   # is_active:bool |None=None
   # is_verified:bool |None=None

class UserResponse(BaseModel):
    id:int
    email:EmailStr
    full_name:str
    phone_number:Optional[str]
    is_active:bool
    is_verified:bool
    role:str
    class config:
        from_attributes =True