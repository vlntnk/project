import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException

from database.db_models import Users, Cookies, OneTimeSales, RepeatedSales


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user_dal(self, name: str, surname: str, email: str, password: str,
                              categories: List[str]) \
            -> Optional[Users]:
        user = Users(name=name, surname=surname, email=email, hashed_password=password,
                     categories=categories)
        try:
            self.db_session.add(user)
            await self.db_session.flush()
            return user
        except Exception as error:
            await self.db_session.rollback()  # почему-то было закомментрованно
            return None

    async def get_user_by_email_dal(self, email: str) -> Optional[Users]:
        query = select(Users).where(Users.email == email)
        try:
            db_response = await self.db_session.execute(query)
            return db_response.fetchone()[0]
        except Exception:
            return None

    async def delete_user_dal(self, user_id: UUID) -> Optional[bool]:
        query = select(Users).where(Users.user_id == user_id)
        user = await self.db_session.execute(query)
        if user:
            query = delete(Users).where(Users.user_id == user_id)
            try:
                await self.db_session.execute(query)
                await self.db_session.flush()
            except Exception:
                return None
            else:
                return True

    async def update_user_dal(self, user_id: str, **kwargs) -> Optional[UUID]:
        query = (
            update(Users)
            .where(Users.user_id == user_id)
            .values(kwargs)
            .returning(Users)
        )
        try:
            res = await self.db_session.execute(query)
            await self.db_session.flush()
        except Exception as e:
            print(f"{e}")
            raise HTTPException(status_code=406, detail=e)
        update_user_id_row = res.fetchone()
        if update_user_id_row is not None:
            return update_user_id_row[0]

    async def add_to_cookie_dal(self, session_id: str, token: str):
        cookie = Cookies(session_id=session_id, jwt_token=token)
        try:
            self.db_session.add(cookie)
            await self.db_session.flush()
            return cookie
        except Exception as e:
            await self.db_session.rollback()
            raise Exception  # Поменять все ошибки

    async def get_from_cookie(self, got_id: str):
        query = select(Cookies).where(Cookies.session_id == got_id)
        try:
            cookie_record = await self.db_session.execute(query)
            return cookie_record.fetchone()[0]
        except Exception as e:
            print(f"{e}")
            return None

    # async def add_categories(self, categories):
        

class SalesDAL:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def write_one_time_sale(self, sale_data):
        sale = OneTimeSales(percentage=sale_data.percentage, comment=sale_data.comment,
                            end_at=sale_data.end_at, date=sale_data.date,
                            categories=sale_data.categories, creator=sale_data.creator,
                            coordinates=sale_data.coordinates)
        try:
            self.session.add(sale)
            await self.session.flush()
            return sale
        except Exception:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail='database error')

    async def write_repeated_sale(self, sale_data):
        sale = RepeatedSales(percentage=sale_data.percentage, comment=sale_data.comment,
                             start_at=sale_data.start_at, end_at=sale_data.end_at,
                             weekday=sale_data.weekday, categories=sale_data.categories,
                             creator=sale_data.creator, coordinates=sale_data.coordinates)
        try:
            self.session.add(sale)
            await self.session.flush()
            return sale
        except Exception:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail='database error')

    async def read_all_sales(self):
        try:
            query_onetime = select(OneTimeSales)
            # query_repeated = select(RepeatedSales)
            response = await self.session.execute(query_onetime)
            await self.session.flush()
            print(response, 'get all sales dal')
            return response.scalars().all()
        except Exception as e:
            print(f"{e}")
            raise e


