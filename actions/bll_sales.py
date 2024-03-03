from database.dal import SalesDAL


async def _create_one_time_sale(session, sale_data):
    async with session.begin():
        dal_object = SalesDAL(session)
        sale = await dal_object.write_one_time_sale(sale_data)
        return sale


async def _create_repeated_sale(session, sale_data):
    async with session.begin():
        dal_object = SalesDAL(session)
        sale = await dal_object.write_repeated_sale(sale_data)
        return sale

