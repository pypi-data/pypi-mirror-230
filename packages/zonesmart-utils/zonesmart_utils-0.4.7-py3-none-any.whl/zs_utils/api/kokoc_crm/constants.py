from model_utils import Choices


CRM_CATEGORIES = Choices(
    ("23", "LANDING", "Лендинг"),
    ("25", "OMS_AND_ADS", "ЕЛК + Реклама"),
)

CRM_LANDING_STAGES = Choices(
    ("C23:UC_N6MLFK", "NEW", "Неразобранные"),
    ("C23:NEW", "NEW_CONTACT_TRY", "Повторная попытка связаться"),
    ("C23:PREPARATION", "REQUEST_REPEAT", "Повторная заявка"),
    ("C23:PREPAYMENT_INVOIC", "FIRST_CONTACT", "Первичный контакт"),
    ("C23:EXECUTING", "FIRST_CALL_PREPARATION", "Подготовка к первому звонку"),
    ("C23:FINAL_INVOICE", "NEGOTIATION", "Переговоры"),
    ("C23:UC_YJ9K20", "DECISION_MAKING", "Принятие решения"),
    ("C23:UC_5RE0RY", "CONTRACT_SIGNING", "Подписание договора"),
    ("C23:UC_3FJIKP", "PAYMENT", "Оплата"),
    ("C23:UC_LJJ3G0", "ON_HOLD", "On Hold"),
    ("C23:WON", "DEAL_SUCCESS", "Сделка успешна"),
    ("C23:LOSE", "DEAL_FAIL", "Сделка провалена"),
    ("C23:APOLOGY", "DEAL_FAIL_ANALYSIS", "Анализ причины провала"),
)

CRM_OMS_AND_ADS_STAGES = Choices(
    ("C25:NEW", "NEW", "Новый запрос от клиента"),
    ("C25:PREPARATION", "PROCESSING", "Запрос в работе"),
    ("C25:WON", "COMPLETED", "Запрос выполнен"),
    ("C25:LOSE", "CANCELED", "Запрос отменен"),
)

CRM_OBJECTS = Choices(
    ("CONTACT", "Контакт"),
    ("DEAL", "Сделка"),
    ("STATUS", "Статус"),
)

CRM_ACTIVITY_TYPES = Choices(
    (1, "MEETING", "Встреча"),
    (2, "CALL", "Звонок"),
    (3, "TASK", "Задача"),
    (4, "MESSAGE", "Письмо"),
    (5, "ACTION", "Действие"),
)
