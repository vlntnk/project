from pydantic import (BaseModel, EmailStr, field_validator,
                      ConfigDict, constr)
from fastapi import HTTPException
from typing import Optional, Tuple, List, Union
import re
from uuid import UUID
from datetime import time, date
from decimal import Decimal

LETTER_MATCH_PATTERN = re.compile(r'^[A-ZА-Я\-]+$', re.IGNORECASE)


class CreateUser(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str
    categories: List[str]

    @field_validator('name')
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail='Name must contain only letters'
            )
        return value

    @field_validator('surname')
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail='Surname must contain only letters'
            )
        return value


class TunedModel(BaseModel):
    class Config:
        from_attributes = True


class CreateUser_Response(TunedModel):
    name: str
    surname: str
    email: EmailStr
    token: str
    type: str = 'Bearer'


class AuthUser_Request(BaseModel):
    model_config = ConfigDict(strict=True)

    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class ShowUser(BaseModel):
    user_id: str | None
    name: str
    surname: str
    email: EmailStr


class DeleteUser_Request(BaseModel):
    password: str


class UpdateUser_Request(BaseModel):
    name: Optional[constr(min_length=1)]
    surname: Optional[constr(min_length=1)]
    email: EmailStr | None
    categories: Optional[List[str]]
    notifications: Optional[bool]
    radius: Optional[int]

    @field_validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value

    @field_validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contains only letters"
            )
        return value


class Cookie_model(BaseModel):
    session_id: UUID
    jwt_token: str


# SALES
class OneTimeSaleRequest(BaseModel):
    percentage: int
    comment: Optional[str]
    end_at: time
    date: date
    categories: List[str]
    creator: EmailStr
    coordinates: Tuple[Decimal, Decimal]


class RepeatedSaleRequest(BaseModel):
    percentage: int
    comment: Optional[str]
    start_at: time
    end_at: time
    weekday: str
    categories: List[str]
    creator: EmailStr
    coordinates: Tuple[Decimal, Decimal]


class CategoriesRequest(BaseModel):
    categories: List[str]


class ChangeRadiusRequest(BaseModel):
    radius: int


class SaleResponse(BaseModel):
    id: UUID


class GetOneTime(BaseModel):

    id: UUID
    percentage: int
    comment: Optional[str]
    start_at: time
    end_at: time
    # weekday: Optional[Union[str, date]]
    date: date
    categories: List[str]
    creator: EmailStr
    coordinates: List[Decimal]


class GetRepeated(BaseModel):

    id: UUID
    percentage: int
    comment: Optional[str]
    start_at: time
    end_at: time
    weekday: str
    # date: Optional[date]
    categories: List[str]
    creator: EmailStr
    coordinates: List[Decimal]


class GetSales(BaseModel):
    id: UUID
    percentage: int
    coordinates: Tuple[Decimal, Decimal]
