from database.dal import SalesDAL
from actions.bll_login import get_data_from_cookie
from jwt_token.generate_jwt import decode_jwt


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

