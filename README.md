# mini-CRM
Тестовое задание  "Менеджер задач" с тестами


Стек проекта:

Python\
FastAPI\
SQLite\
SQLAlchemy\
Alembic (миграции)\
Poetry\
Ruff, Pyright, isort\
Docker и Docker-compose


Как запустить:

С помощью uvicorn:
```
uvicorn app.main:app
```
С помощью Docker-compose:
```
docker compose build
docker compose up
```
Всё работает на 8000 порте

Структура проекта:
```

```
Предметная область:
```
1.Оператор
Активен / не активен (может или не может получать новые обращения).
Имеет лимит по максимальному количеству «активных» лидов/обращений
(формулировку и реализацию активности вы выбираете сами).
Для каждого источника (бота), с которым он работает, имеет числовой вес
(компетенцию / долю трафика).
Пример: для источника A оператор1 — вес 10, оператор2 — вес 30 → примерно
25% и 75% трафика соответственно.
```

Реализовано через модель Operators:
```
class Operators(Base):
    __tablename__ = "operators"

    status: Mapped[int] = mapped_column(default=0, nullable=False)
    limit_of_contacts: Mapped[int] = mapped_column(nullable=False)
```
Где:
```
status: (0/1) отвечает за активное/неактивное состояние оператора;
limit_of_contacts: отвечает за лимит в обращениях на одного оператора
```


```
2.Лид
Представляет одного конечного клиента.
Один и тот же лид может написать через несколько разных ботов/источников.
Должен быть способ однозначно понять, что обращения относятся к одному и тому
же лиду (например, общий внешний идентификатор, телефон, email и т.п. — на
ваше усмотрение).
```

Реализовано через модель Clients:
```
class Clients(Base):
    __tablename__ = "clients"

    email: Mapped[str] = mapped_column(unique=True, nullable=False)
```
Где:
```
email: отвечает за роль внешнего идентификатора
```


```
3.Источник / бот
Канал, из которого пришло обращение (один из условных «30 ботов»).
Для каждого источника задаётся конфигурация, какие операторы его обслуживают
и с какими весами.
```

Реализовано через модель Bots:
```
class Bots(Base):
    __tablename__ = "bots"

    operators: Mapped[dict[int, int]] = mapped_column(JSON, nullable=True, default={})
```
Где:
```
operators: словарь вида {оператор: вес}, отвечает за информацию об операторах для этого источника и их трафике
```

```
4. Обращение / контакт
Конкретный факт, что лид написал из определённого источника.
При создании обращения система должна:
связать его с лидом (найти существующего или создать нового),
определить источник,
выбрать и назначить оператора по правилам ниже,
сохранить результат.
```

Реализовано через модель Contacts:
```
class Contacts(Base):
    __tablename__ = "contacts"

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    bots_id: Mapped[int] = mapped_column(ForeignKey("bots.id"), nullable=False)
    operator_id: Mapped[int] = mapped_column(ForeignKey("operators.id"), nullable=False)
```
Где:
```
client_id: связь с лидом по ID
bots_id: связь с ботом по ID
operator_id: связь с оператором по ID
```


Бизнес-логика распределения обращений:
```
1.Определить лида
По входным данным найти существующего лида.
Если такой лид не найден — создать нового.
```

Реализовано в ендпоинте при создании обращения:
```
client = await ClientsDAO.find_one_or_none(session=session, email=client_email)
    if not client:
        client = await ClientsDAO.add(
            session=session,
            email=client_email,
        )
```

```
2.Определить доступных операторов для источника
Найти всех операторов, назначенных на данный источник (бот) в конфигурации.
Отфильтровать операторов по условиям:
оператор активен;
его текущая нагрузка не превышает лимит (по количеству активных лидов/
обращений — на ваше усмотрение, главное описать в README, что именно
вы считаете нагрузкой).
3. Распределить с учётом весов (процентного соотношения)
У каждого оператора для этого источника есть числовой вес (например, 10, 20, 50
и т.д.).
Нужно выбирать оператора таким образом, чтобы доля обращений в среднем
соответствовала этим весам.
Допустимые варианты:
случайный выбор с вероятностью вес / сумма_весов среди подходящих
операторов;
детерминированный алгоритм, который по истории обращений старается
выдерживать заданные доли.
При этом оператор не должен превышать лимит нагрузки: если оператор
«выиграл», но его лимит уже исчерпан, нужно выбрать другого подходящего или
признать, что подходящих нет.
```

Логика распределения по весам частями обрабатывается в файле app.contacts.utils, а проверка на лимит и активность происходит в файле app.contacts.dao

Для распределения по весам выбран алгоритм:
```
случайный выбор с вероятностью вес / сумма_весов среди подходящих
операторов;

async def weighted_random_choice(operators, weights):
    """
    Случайный выбор оператора с учетом весов
    """
    if not operators:
        return
    return int(random.choices(operators, weights=weights, k=1)[0])
```

```
4.Создать обращение
Связать обращение с:
лидом,
источником,
назначенным оператором (если он найден).
Если подходящих операторов нет:
можно создать обращение без оператора,
либо вернуть 4xx-ошибку.
Выберите один вариант и опишите его в README.
```

Если подходящих вариантов нет, клиенту возвращается 409 ошибка
```
class NotOperatorForYourContact(BaseAppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Not operator for your contact"
```

API:

Создание оператора.
```
@router.post("/add")
async def add_operator(
    session: DbSession, limit_of_contacts: int = Query(gt=0)
) -> SOperators:
    operator = await OperatorsDAO.add(
        session=session, limit_of_contacts=limit_of_contacts
    )
    return operator
```
Просмотр списка операторов.
```
@router.get("/all")
async def get_all_operators(session: DbSession) -> List[SOperators]:
    operators = await OperatorsDAO.find_all(session=session)

    return operators
```
Управление лимитом нагрузки и активностью оператора.
```
@router.patch("/update_status")
async def update_operator_status(
    session: DbSession,
    operator_id: int,
    status: int = Literal[0, 1],  # pyright: ignore [reportArgumentType]
) -> SOperators:
    operator = await OperatorsDAO.find_by_id(session=session, model_id=operator_id)
    if not operator:
        raise NotOperatorWithThisId

    operator = await OperatorsDAO.update(
        session=session, model_id=operator_id, status=status
    )
    return operator


@router.patch("/update_limit")
async def update_operator_limit_of_contacts(
    session: DbSession,
    operator_id: int,
    limit_of_contacts: int = Query(gt=0),
) -> SOperators:
    operator = await OperatorsDAO.find_by_id(session=session, model_id=operator_id)
    if not operator:
        raise NotOperatorWithThisId

    operator = await OperatorsDAO.update(
        session=session, model_id=operator_id, limit_of_contacts=limit_of_contacts
    )
    return operator
```
Создание источника (бота).
```
@router.post("/add")
async def add_bot(session: DbSession) -> SBots:
    bot = await BotsDAO.add(session=session)
    return bot
```
Настройка для источника списка операторов и их весов (процентного
распределения).
Это может быть отдельный эндпоинт или часть CRUD по источнику/оператору
```
@router.patch("/update_operators")
async def update_operators(
    session: DbSession, bot_id: int, operator_id: int, weight: int
) -> SBots:
    operator = await OperatorsDAO.find_by_id(session=session, model_id=operator_id)
    if not operator:
        raise NotOperatorWithThisId

    bot = await BotsDAO.find_by_id(session=session, model_id=bot_id)
    if not bot:
        raise NotBotWithThisId

    updated_bot = await BotsDAO.update_bot_operators(
        session=session, bot_id=bot_id, operator_id=operator_id, weight=weight
    )

    return updated_bot
```
Эндпоинт, принимающий данные:
идентификатор лида (или данные, по которым его можно определить/
создать),
идентификатор источника (бота),
дополнительные данные обращения по вашему усмотрению.
Внутри:
найти/создать лида,
выбрать оператора по описанным правилам,
создать обращение.
В ответ вернуть информацию об обращении и назначенном операторе (если есть).
```
@router.post("/add")
async def add_contact(session: DbSession, client_email: str, bot_id: int) -> SContacts:
    bot = await BotsDAO.find_by_id(session=session, model_id=bot_id)
    if not bot:
        raise NotBotWithThisId

    if bot.operators == {}:
        raise NotOperatorForYourContact

    client = await ClientsDAO.find_one_or_none(session=session, email=client_email)
    if not client:
        client = await ClientsDAO.add(
            session=session,
            email=client_email,
        )

    new_contact = await add_contact_for_operator(
        session=session,
        operators=bot.operators.keys(),
        weights=bot.operators.values(),
        client_id=client.id,  # pyright: ignore [reportOptionalMemberAccess]
        bot_id=bot_id,
    )
    if not new_contact:
        raise NotOperatorForYourContact

    return new_contact
```
```Дополнительных данных не делал, так как рассматриваю проект в абстракции```

Эндпоинты для просмотра:

списка лидов и их обращений,
```
@router.get("/all")
async def get_all_clients(session: DbSession) -> List[SClients]:
    all_clients = await ClientsDAO.find_all(session=session)
    return all_clients
```
```
@router.get("/{client_id}")
async def get_contacts_by_client_id(
    session: DbSession, client_id: int
) -> List[SContacts]:
    contacts = await ContactsDAO.find_all(session=session, client_id=client_id)

    return contacts
```
распределения обращений по операторам и источникам (хотя бы в простом
виде, чтобы было понятно, что один лид может иметь несколько обращений
из разных источников).
```
Не до конца понял, что здесь надо сделать, но проверить, что один лид может иметь несколько обращений
из разных источников, можно с помощью этих ендпоинтов:
```
```
@router.get("/{client_id}")
async def get_contacts_by_client_id(
    session: DbSession, client_id: int
) -> List[SContacts]:
    contacts = await ContactsDAO.find_all(session=session, client_id=client_id)

    return contacts
```
```
@router.get("/all/")
async def get_all_contacts(session: DbSession) -> List[SContacts]:
    all_contacts = await ContactsDAO.find_all(session=session)

    return all_contacts
```


описание алгоритма распределения:
как определяется, что обращения принадлежат одному и тому же лиду,
```
Это не особо нужно в моём проекте, но в любом случае можно по ID/Email
```
как учитываются веса операторов по источникам,
```
Не понял про что здесь, веса учитываются как int, шанс "выпадения" оператора находится по формуле:
```
 ```
вес оператора/сумма весов * 100
```
как учитываются лимиты нагрузки,
```
По кол-ву вместе взятых действительных обращений на одного оператора 
```
что происходит, если подходящих операторов нет.
```
Клиенту возвращается ошибка 409 (я посчитал ёё наиболее правильной)
```