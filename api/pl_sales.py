from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from api.validate_models import OneTimeSaleRequest, SaleResponse, RepeatedSaleRequest
from actions.bll_sales import _create_one_time_sale, _create_repeated_sale
from actions.bll_login import get_cookie_id

sales_router = APIRouter()


@sales_router.post('/one_time_sale')
async def add_one_time_sale(sale: OneTimeSaleRequest,
                            session: AsyncSession = Depends(get_db),
                            cookie_id=Depends(get_cookie_id)):
    server_response = await _create_one_time_sale(session, sale, cookie_id)
    if server_response is None:
        return HTTPException(status_code=500, detail='database error')
    return SaleResponse(
        id=server_response.id)


@sales_router.post('/repeated_sale')
async def add_repeated_sale(sale: RepeatedSaleRequest,
                            session: AsyncSession = Depends(get_db),
                            cookie_id=Depends(get_cookie_id)):
    server_response = await _create_repeated_sale(session, sale, cookie_id)
    if server_response is None:
        return HTTPException(status_code=500, detail='database error')
    return SaleResponse(
        id=server_response.id)


