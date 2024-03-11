from fastapi import HTTPException
from functools import reduce

from database.dal import SalesDAL
from actions.bll_login import get_data_from_cookie
from jwt_token.generate_jwt import decode_jwt
from api.validate_models import GetSales


async def _create_one_time_sale(session, sale_data, cookie_id):
    cookie_data = await get_data_from_cookie(session, cookie_id)
    email = decode_jwt(cookie_data.jwt_token)['email']
    sale_data.creator = email
    async with session.begin():
        dal_object = SalesDAL(session)
        sale = await dal_object.write_one_time_sale(sale_data)
        return sale


async def _create_repeated_sale(session, sale_data, cookie_id):
    cookie_data = await get_data_from_cookie(session, cookie_id)
    email = decode_jwt(cookie_data.jwt_token)['email']
    sale_data.creator = email
    async with session.begin():
        dal_object = SalesDAL(session)
        sale = await dal_object.write_repeated_sale(sale_data)
        return sale


async def _get_all_sales(session):
    async with session.begin():
        dal_object = SalesDAL(session)
        result = await dal_object.read_all_sales()
        print(result, 'get all sales bll')
        if result is None:
            raise HTTPException(status_code=500, detail='database error')
        return result


async def _get_certain_sale(session, sale_id):
    async with session.begin():
        dal_object = SalesDAL(session)
        sale = await dal_object.get_certain_sale_dal(sale_id)
        return sale


async def _get_sales_by_email(session, cookie_id):
    cookie_data = await get_data_from_cookie(session, cookie_id)
    email = decode_jwt(cookie_data.jwt_token)['email']
    async with session.begin():
        dal_object = SalesDAL(session)
        try:
            sales = await dal_object.get_sales_by_email(email)
        except Exception as e:
            raise e
        else:
            response = []
            for index, sale in enumerate(sales):
                response.append(GetSales.model_validate(sale, from_attributes=True))
            print(response, 'response bll')
            return response

async def _get_sales_by_categories(session, cookie_id):
    data = await get_data_from_cookie(session, cookie_id)
    user_id = decode_jwt(data.jwt_token)['sub']
    async with session.begin():
        dal_object = SalesDAL(session)
        sales = await dal_object.get_sales_by_categories(user_id)
        response = []
        for sale in sales:
            response.append(GetSales.model_validate(sale, from_attributes=True))
        return response