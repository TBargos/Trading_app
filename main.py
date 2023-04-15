from datetime import datetime   # Ну, этот импорт умеет собирать в определённом стиле строку из дата-времени
from enum import Enum  # позволяет задавать своеобразные константы. Часто называются множествами
from typing import List, Dict, Optional # очень помогает определять вложенные типы
# например, List имеет ввиду что-то итерируемое, словарь, тьюпл или лист, но внутри листа может быть всё, что угодно
# Optional значит "либо это, либо Null". Хотя python запросто допускает что-то вроде value: Optional[int] = "stringer"

from fastapi import FastAPI
from pydantic import BaseModel, Field
# BaseModel нужен для задания сложных или вложенных друг в друга типов через поля класса. Хороший пример класс Trade
# где-то внизу. Field в type hint нужен для отлова несоответствий. Скажем, нам нужно значение меньше или равно 0,
# если отправить -1. то сервер вернёт клиенту вполне адекватный текст ошибки.

app = FastAPI(
    title="Test app"
)  # просто экземпляр FastAPI


fake_users = [
    {"id": 1, "role": "admin", "name": "Bob"},
    {"id": 2, "role": "investor", "name": "John"},
    {"id": 3, "role": "trader", "name": "Matt"},
    {"id": 4, "role": "investor", "name": "Homer", "degree": [
        {"id": 1, "created_at": "2020-01-01T00:00:00", "type_degree": "expert"}
    ]}
]


class DegreeType(Enum):
    newbie = "newbie"
    expert = "expert"


class Degree(BaseModel):
    id: int
    created_at: datetime
    type_degree: DegreeType


class User(BaseModel):
    id: int
    role: str
    name: str
    degree: Optional[List[Degree]] = []


# response_model. В обычных функциях есть возможность аннотировать тип возврата через -> int (например)
# но это лишь для понятности кода, для интерпретатора это не критично, может выводить подсказки и предупреждения,
# но не признаёт это ошибкой. Тут приходит на помощь параметр response_model из модуля FastAPI (fastapi)
# если на возврат будет отправлено что-то, что не соответствует описанию вложенного типа (класс-наследник BaseModel)
# то клиент хотя бы получит сообщение о внутренней ошибке сервера
@app.get('/users/{user_id}', response_model=List[User])
def get_user(user_id: int):
    return [user for user in fake_users if user.get("id") == user_id]


fake_trades = [
    {"id": 1, "user_id": 1, "currency": "BTC", "side": "buy", "price": 123, "amount": 2.12},
    {"id": 2, "user_id": 1, "currency": "BTC", "sell": "buy", "price": 125, "amount": 2.12}
]


@app.get("/trades")
def get_trades(limit: int = 1, offset: int = 0):
    return fake_trades[offset:][:limit]  #  два отсечения, сначала слева, потом с конца


# Модель данных
class Trade(BaseModel):  # объект такого класса будет содержать поля, но не листом или словарём, а как поля объекта
    id: int
    user_id: int
    currency: str = Field(max_length=5)  # Field импортирован из pydantic, аргументом может принимать ограничители
    side: str
    price: float = Field(ge=0)  # например, больше или равно 0
    amount: float


@app.post("/trades")
def add_trades(trades: List[Trade]):
    fake_trades.extend(trades)
    return {"status": 200, "data": fake_trades}
