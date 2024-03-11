from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from pydantic import EmailStr

from database.session import get_db
from database.db_models import OneTimeSales, RepeatedSales
from api.validate_models import (OneTimeSaleRequest, SaleResponse, RepeatedSaleRequest, GetSales,
                                 GetOneTime, GetRepeated)
from actions.bll_sales import (_create_one_time_sale, _create_repeated_sale,
                               _get_all_sales, _get_certain_sale, _get_sales_by_email,
                               _get_sales_by_categories)
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
    # response = []
    # for record in db_response:
    #     for row in record:
    #         # Предполагается, что row - это экземпляр модели SQLAlchemy
    #         # Преобразуйте row в соответствующую модель Pydantic
    #         print(row, 'Row object')
    #         model = GetSalesResponse.model_validate(row, from_attributes=True)
    #         print(model, 'model get all sales pl')
    #         # Добавьте модель в список ответов
    #         response.append(model.dict())
    try:
        response = []
        for index, db_object in enumerate(db_response):
            for record in db_object:
                print(type(record))
                # if isinstance(record, OneTimeSales):
                #     print('yes')
                response.append(GetSales.model_validate(record, from_attributes=True))
                # elif isinstance(record, RepeatedSales):
                #     print('yes')
                #     response.append(GetSales.model_validate(record, from_attributes=True))
        print(response)
        return response
    except Exception as e:
        print(f'{e}')
        return HTTPException(status_code=500, detail=f'{e}')


@sales_router.get('/get_sale/{sale_id}')
async def get_certain_sale(sale_id: UUID, session: AsyncSession = Depends(get_db)):
    sale = await _get_certain_sale(session, sale_id)
    print(type(sale))
    print(sale)
    if isinstance(sale, OneTimeSales):
        return GetOneTime.model_validate(sale, from_attributes=True)
    elif isinstance(sale, RepeatedSales):
        return GetRepeated.model_validate(sale, from_attributes=True)
    else:
        return Response('no such sale', media_type='application/json')


@sales_router.get('/my_sales')
async def get_sales_by_email(cookie_id=Depends(get_cookie_id), session: AsyncSession = Depends(get_db)):
    # try:
        response = await _get_sales_by_email(session, cookie_id)
    # except Exception as e:
    #     return e
    # else:
        return {'sales': response}

@sales_router.get('/favourite')
async def get_favourite(cookie_id = Depends(get_cookie_id), session: AsyncSession = Depends(get_db)):
    sales = await _get_sales_by_categories(session, cookie_id)
    return {'sales': sales}
