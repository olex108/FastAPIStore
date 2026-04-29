import xlsxwriter
from pathlib import Path
from src.config.settings import get_settings
from src.schemas.cart import CartOut
from src.models.cart import Cart
from src.models.order import Contacts
from src.models.user import User

settings = get_settings()


def generate_receipt_excel(cart_data: CartOut, contacts_data: Contacts, user_info: User) -> str:
    """
    Создает Excel файл заказа и сохраняет его в папку media/orders.
    Возвращает относительный путь к файлу.
    """

    # 1. Подготовка папки
    orders_dir = Path(settings.BASE_DIR) / "media" / "orders"
    orders_dir.mkdir(parents=True, exist_ok=True)

    formatted_date = cart_data.order_at.strftime('%Y-%m-%d_%H-%M-%S')

    file_name = f"receipt_{formatted_date}_{cart_data.id}.xlsx"
    file_path = orders_dir / file_name

    workbook = xlsxwriter.Workbook(str(file_path))
    worksheet = workbook.add_worksheet("Чек")

    # Стили
    bold = workbook.add_format({'bold': True})
    money = workbook.add_format({'num_format': '#,##0.00'})
    header_style = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})

    # 2. Шапка документа и реквизиты заказчика
    worksheet.write('A1', f'Заказ №: {cart_data.id}/{formatted_date}', bold)
    worksheet.write('A2', f'Дата заказа: {formatted_date}')
    worksheet.write('A4', 'Реквизиты компании:', bold)

    try:
        worksheet.write('A5', f'{contacts_data.name or "Не указана"}')
        worksheet.write('A6', f'ИНН {contacts_data.inn or "Не указана"}')
        worksheet.write('A7', f'{contacts_data.address or "Не указана"}')
    except Exception:
        worksheet.write('A5', f'{"Не указана"}')

    worksheet.write('D4', 'Реквизиты заказчика:', bold)
    worksheet.write('D5', f'ФИО: {user_info.full_name}')
    worksheet.write('D6', f'Тел: {user_info.phone}')
    worksheet.write('D7', f'Email: {user_info.email}')

    # 3. Таблица товаров
    table_headers = ["№", "ID товара", "Название", "Кол-во", "Цена", "Сумма"]
    for col, text in enumerate(table_headers):
        worksheet.write(9, col, text, header_style)

    row = 10
    for idx, item in enumerate(cart_data.products, start=1):

        worksheet.write(row, 0, idx)
        worksheet.write(row, 1, item.product.id)  # Нужно добавить в схему или вытащить из вложенной
        worksheet.write(row, 2, item.product.name)
        worksheet.write(row, 3, item.product_quantity)
        worksheet.write(row, 4, item.product_price, money)
        worksheet.write(row, 5, item.product_amount, money)
        row += 1

    # 4. Итого
    worksheet.write(row + 1, 4, "Сумма заказа:", bold)
    worksheet.write(row + 1, 5, cart_data.amount, money)

    workbook.close()

    # Возвращаем относительный путь для БД
    return f"media/orders/{file_name}"
