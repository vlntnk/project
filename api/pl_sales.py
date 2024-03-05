from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from database.db_models import OneTimeSales
from api.validate_models import (OneTimeSaleRequest, SaleResponse, RepeatedSaleRequest,
                                 GetSalesResponse)
from actions.bll_sales import (_create_one_time_sale, _create_repeated_sale,
                               _get_all_sales)
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


@sales_router.get('/get_all')
async def get_all_sales(session: AsyncSession = Depends(get_db)):
    # try:
    #     print(12)
    db_response = await _get_all_sales(session)
    print(db_response, 'db response get all sales pl')
    # except Exception as e:
    #     return HTTPException(status_code=500, detail=f'{e}')
    response = []
    # for record in db_response:
    #     for row in record:
    #         # Предполагается, что row - это экземпляр модели SQLAlchemy
    #         # Преобразуйте row в соответствующую модель Pydantic
    #         print(row, 'Row object')
    #         model = GetSalesResponse.model_validate(row, from_attributes=True)
    #         print(model, 'model get all sales pl')
    #         # Добавьте модель в список ответов
    #         response.append(model.dict())
    response = [GetSalesResponse.model_validate(row, from_attributes=True) for row in db_response]
    return response

