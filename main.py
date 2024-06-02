from typing import Union
import func
from fastapi import FastAPI
import markdown2
from fastapi.responses import HTMLResponse
from pprint import pprint
import kontur
import keys
from datetime import datetime
import requests
import base64


from template_base import template_finder, template_finder_ip

AUTH = keys.API_KEY

app = FastAPI()

# uvicorn main:app --host 95.152.289.9 --reload


@app.post("/reference/get/brief_report/")
def send_report_to_company(auth: str, company_id: int, inn: str, folder_id):
    if auth != AUTH:
        return 'invalid auth_token'
    print(auth, company_id, inn, folder_id)

    # Создание подпапки для хранения отчетов из reference
    print('Создаю папку')
    folder_title = func.get_current_datetime()
    print (folder_title)
    folder = func.addsubfolder(folder_id.strip('_'), f'Выгрузка reference_фокус {str(folder_title)}')
    print('Создана папка ID:', folder['ID'])

    # Получение данных их контура
    print('получаю данные из контура')
    kontur_auth = keys.KONTUR_KEY
    print('получаю briefReportPdf')
    briefReportPdf = kontur.download_pdf_express(f'https://focus-api.kontur.ru/api3/briefReport?key={kontur_auth}&inn={inn}&pdf=value', 'Экспресс-отчет по контрагенту.pdf')
    print('получаю finan')
    finan = kontur.download_pdf_express(f'https://focus-api.kontur.ru/api3/finan?key={kontur_auth}&inn={inn}', 'Финансовый анализ.pdf')
    print('получаю excerpt')
    excerpt = kontur.download_pdf_express(f'https://focus-api.kontur.ru/api3/excerpt?key={kontur_auth}&inn={inn}', 'Выписка из ЕГРЮЛ/ЕГРИП.pdf')

    # Отправка файлов в Б24
    print('отправляю файлы в б24')
    send_results = []
    for i in [briefReportPdf, finan, excerpt]:
        print('Загрузка', i['title'])
        upload = func.upload_file(i['base64_file'], i['title'], folder['ID'])
        send_results.append([f"{upload['ID']}_{i['title']}", i['base64_file']])
        file = i['base64_file']
        print(upload)

    print('Гружу коммент')
    today = datetime.now()
    func.b.call('crm.timeline.comment.add', {
        'fields':{
            'ENTITY_ID': company_id,
            'ENTITY_TYPE': 'company',
            'COMMENT': f'🎩 Выгрузка контур фокус от {datetime.today().strftime("%Y-%m-%d")}',
            'FILES': send_results,
            'AUTHOR_ID': '1'
            }
    })

    # print('готово')



'''
    file_in_base64 = file['base64_file']
    file_name = 'report.pdf'
    upload = func.upload_file(file_in_base64, file_name, folder_id)'''


@app.post("/element_add/")
def element_add(auth: str, massiv: dict):
    '''
        # Метод для создания карточки смарт процесса

        Тело запроса принимает на вход массив вида:

        ### Пример запроса

        ```json
        {
            "Номер документа в 1С": "123",
            "Карточка Контрагента": ["Карточка.txt", "0JTQvtC60YPQvNC10L3Rgg=="],
            "Тип контрагнета": "Юридическое лицо",
            "Контактное лицо на стороне контрагента": "408",
            "ИНН Контрагента в 1С": "1234567",
            "Копия решения о назначении руководителя или копия приказа о назначении руководителя":
                ["Приказ.pdf", "0JTQvtC60YPQvNC10L3Rgg=="],
            "Копия устава (первая, последняя страницы и страница с полномочиями руководителя)":
                ["Устав.txt", "0JTQvtC60YPQvNC10L3Rgg=="],
            "Копия паспорта (страница с фотографией, регистрацией по месту жительства)":
                ["Паспорт.pdf", "0JTQvtC60YPQvNC10L3Rgg=="],
            "Копия Свидетельства о внесении записи в ЕГРИП":
                ["Свидетельсво_егрип.txt","0JTQvtC60YPQvNC10L3Rgg=="],
            "Копия Свидетельства о постановке на учет в налоговом органе (ИНН)": ["Свидетельство_ИНН.txt", "0JTQvtC60YPQvNC10L3Rgg=="],
            "Доверенность на уполномоченное лицо при подписании договора":
                ["Доверенность.pdf","0JTQvtC60YPQvNC10L3Rgg=="]
        }
        ```
        Полный список доступных полей, в данный момент в разработке, будет доступен по адресу /docs/fields
        ---

        # Ответ

        При успешной обработке, в ответ отдаст массив вида:
        ```
        {
        "auth": "111",
        "massiv": {
            "Номер документа в 1С": "123",
            "Карточка Контрагента": [
            "Карточка.txt",
            "0JTQvtC60YPQvNC10L3Rgg=="
            ]
        },
        "result": "Результат обработки запроса"
        }
        ```
        ## Правила обработки полей для вложений

        - Содержание файла закодировать кодировкой `base64`

        - В поле для вложения, передавать массив вида `["Название файла", "Результат кодирования"]`

        ## Правила передачи полей для связи

        Под формулировкой "поле привязки" имеется ввиду поля которые используются битриксом для связки одного элемента CRM с другим
        для подобных полей, в явном виде передаются ID этих элементов на стороне Б24.


    '''

    el = func.b.get_all('crm.item.add',
    {
        'entityTypeId': '162',
        'fields':  {
            'contactId': '408',
            'stageId': 'DT162_6:UC_T2LCT2',
            'ufCrm4_1688739541847': 'ООО Ромашка',
            "ufCrm4_1688737979": '1',
            "ufCrm4_1688738013": '1',
            "ufCrm4_1688738502": '1',
            'ufCrm4_1688738829061': '123',
            'ufCrm4_1688738862887': '12345678910',
            'ufCrm4_1688739593576': '28',
            'ufCrm4_1688740462693': ['Карточка.txt', '0JTQvtC60YPQvNC10L3Rgg=='],
            'ufCrm4_1688744581761': ['Приказ.pdf', '0JTQvtC60YPQvNC10L3Rgg=='],
            'ufCrm4_1688744595387': ['Устав.txt', '0JTQvtC60YPQvNC10L3Rgg=='],
            'ufCrm4_1688744613533': ['Паспорт.pdf', '0JTQvtC60YPQvNC10L3Rgg=='],
            'ufCrm4_1688744633795': ['Свидетельсво_егрип.txt', '0JTQvtC60YPQvNC10L3Rgg=='],
            'ufCrm4_1688744648168': ['Свидетельство_ИНН.txt', '0JTQvtC60YPQvNC10L3Rgg=='],
            'ufCrm4_1688744699057': ['Доверенность.pdf', '0JTQvtC60YPQvNC10L3Rgg==']}
    })



    result = 'Результат обработки запроса'
    return {
        'auth': auth,
        'massiv': massiv,
        'result': {
            'Элемент смарт процесса': {"ID": el['item']['id']}
        }
    }

@app.post('/lead_fields/')
def lead_fields():
    f = func.b.get_all('crm.lead.fields')
    return f

"""

@app.post("/element_fields_get/")
def element_fields_get():
    '''
    Метод отдает массив полей смарт процесса, для списковых полей, отдает id значений.
    '''
    f =ф func.get_sp_field_names('162')
    return f

@app.post("/contact_person_add/")
def contact_person_add():
    '''
    Создает контакт с параметром "Контактное лицо" возвращает BX_CONTACT_ID
    '''
    return None

"""

@app.post('/reference/check_updates/')
def kontur_checker(auth:str, inn:str, company_id:str):
    '''
    # Проверка данных в контур фокусе по запрашиваемому контрагенту

    ## Как это работает
    - принимает на вход инн контрагента и id компании в которую передавать данные
    - отправляет запросы:
        - companyBankruptcy | Получаем инфу о банкротсве
        - inspections | Получаем инфу о проверках
        - fssp | Получаем инфу про исполнительные произ-ва
        - req | прекращение деятельности

            "Статус организации - status": {
                "Неформализованное описание статуса - statusString": "Действующее"
                },
        - analytics (Расширенная аналитика), в ответе ищет ключи
            - Намерения о банкротсве
                ```
                    "Юр. признаки. Обнаружены сообщения о намерении обратиться в суд с заявлением о банкротстве за последний месяц - m7015": true
                ```
            - Дисквалифицированные лица
                ```
                    "Особые реестры ФНС. ФИО руководителей были найдены в реестре дисквалифицированных лиц (ФНС) или в выписке ЕГРЮЛ - m5008": true,
                ```
            - Ответчик по делам о банкротсве
                ```
                    "Арбитраж. Дела в качестве ответчика. Оценка количества дел за 12 последних месяцев - q2001": 24,
                ```
    - отправляет данные в б24
    '''
    if auth != keys.API_KEY:
        return 'invalid auth'
    print('Получаю данные из контура')
    # Получаем массив методом расширенная аналитика
    analytics = kontur.get_analytics(inn)
    # return analytics
    # Приводим ответ метода расширенной аналитики в человекопонятный вид

    # Для каждого события объявлем переменную
    kontur_bancrot = 'None'
    kontur_discval = 'None'
    kontur_otvetchick = 'None'
    kontur_nalog = 'None'

    # Ищем ключи в массиве, если нашли - изменяем значения переменных
    for i in analytics:
        # Намерение о банкротсве
        if i == 'm7015':
            kontur_bancrot = 'Обнаружены сообщения о намерении обратиться в суд'
            'с заявлением о банкротстве за последний месяц'
        # Намерение о банкротсве
        if i == 'm5008':
            kontur_discval = 'ФИО руководителей были найдены'
            'в реестре дисквалифицированных лиц'
        # Ответчик по делам о банкротстве
        if i == 'q2001':
            kontur_otvetchick = f'Дела в качестве ответчика. Оценка количества дел за 12 последних месяцев: {analytics[i]}'
        # Изменение в налоговом режиме
        if i == 'm7050':
            kontur_nalog = 'Применяет упрощенную систему налогообложения — УСН'
        if i == 'm7051':
            kontur_nalog = 'Применяет автоматизированную упрощенную систему налогообложения — АУСН'
        if i == 'm7052':
            kontur_nalog = 'Является плательщиком единого сельскохозяйственного налога — ЕСХН'

    # Формируем массив данных для отправки в б24
    bx_data = {
        # DEV_KONTUR Банкротство
        'UF_CRM_1692633467146': kontur.get_concurrent_bank_stages(inn),
        # DEV_KONTUR_ исполнительное произ-во
        'UF_CRM_1692633595': kontur.get_fssp_data(inn),
        # DEV_KONTUR_ прекращение деятельности
        'UF_CRM_1692633625': kontur.get_organization_status(inn),
        # DEV_KONTUR_ Намерения о банкротсве
        'UF_CRM_1693778422810': kontur_bancrot,
        # DEV_KONTUR_ дисквалифицированные лица
        'UF_CRM_1693778437483': kontur_discval,
        # DEV_KONTUR_ ответчик по делам о банкротстве
        'UF_CRM_1693778451499': kontur_otvetchick,
        # DEV_KONTUR_ Изменения в налоговом режиме
        'UF_CRM_1693778465284': kontur_nalog,
    }
    print('ответ контура', bx_data)
    print()
    print('Отправляю данные в б24')
    с_upd = func.crm_company_update(company_id, bx_data)
    return с_upd, bx_data


@app.post('/get_lead_info/')
def get_lead_info(LEAD_ID, auth):
    """Возвращает всю информацию по запрашиваемой сущности\n

    ```python
    def crm_lead_get(LEAD_ID):
    lead = b.call(
        'crm.lead.list', {
            'filter': {'ID': LEAD_ID},
            'select': ['PHONE', "*", "UF_"]
        }
    )
    return lead
    ```

    """
    if auth:
        print('Получен запрос на вывод информации по лиду')
        # return func.crm_lead_get(LEAD_ID)


@app.post('/reference/auto_fill_company_by_inn/')
def auto_fill_company_by_inn(company_id, auth, inn):
    """
    # Метод для авто заполнения карточки компании данными из дадаты

    ## Принимает на вход: \n

    - инн компании
    - auth токен
    - id компании
    ---

    ## Логика работы

    - Получаем из Дадаты данные компании по инн
    - Если данные получены:
        - Изменяем название компании в Б24
        - Создаем и заполняем объект реквизита
        - Фиксируем изменения в виде текстового сообщения
        - Отправляем текстовое сообщение в б24 в картточку компании

    - Если данные не  получены:
        - Фиксируем ответ ДАДАТЫ в виде текстового сообщения
        - Отправляем текстовое сообщение в б24 в карточку компании
    ---
    ## Итог отработки
    - Если удалось получить  данные в дадате, в битриксе в карточке компании будет коммент вида:
    ```text
    Процесс автозаполнения карточки компании завершен
    Карточка компании дополнена данными из ФНС
    ```
    - Если не удалось получить  данные в дадате, в битриксе в карточке компании будет коммент вида:
    ```text
    Процесс автозаполнения карточки компании прерван, что-то  сломалось
    {Сообщение об ошибке}
    ```

    """
    print('получен запрос на заполнение реквизитов')
    rq = func.Requisite(company_id=company_id)
    print(rq.rq_generate())
    rq.rq_add()


@app.post('/reference/auto_check_company_by_inn/')
def auto_fill_company_by_inn(company_id, auth, inn):
    """
    # Метод для Проверки реквизитов в карточке компани

    ## Принимает на вход: \n

    - инн компании
    - auth токен
    - id компании
    ---
    ---

    - Сообщение передается в комментарий карточки компании
    """
    rq = func.Requisite(company_id=company_id)
    return rq.rq_diff()

@app.post('/document_generate/')
def document_generate(
    # Токен
    auth,
    # id элемента смарт процесса
    smart_process_id,
    # Формат договора
    # format,
    # Тип компании
    company_type
    ):
    """
    # Метод для генерации документа в Б24

    ### Принимает на вход: \n
        - ID элемента смарт процесса\n
        - Юр. лицо с нашей стороны\n
        - Формат договора\n
            - Предоплата 100 %\n
            - Отсрочка платежа\n
            - Лимит + Отсрочка\n
        - Тип компании\n
            - ИП\n
            - Юр. лицо\n
    ### Отработка:\n
        - По входным данным определяет нужный шаблон\n
        - Генерирует документ по шаблону\n
    ### На выходе:\n
        - Отдает пост вида:\n
            ```\n
            Для карточки дог-ра {Название карточки}\n
            Создан документ по шаблону {Название найденного шаблона}\n
            ```\n
    """
    if auth != AUTH:
        print(auth)
        return 'invalid auth_token'

    print('Получен запрос на создание договора')
    print({
        'smart_process_id': smart_process_id,
        'compny_type': company_type,
    })

    # Получаем карточку смарт процесса
    print('Получаю элемент смарт процесса')
    s_p = func.b.get_all('crm.item.get', {'entityTypeId': '162', 'id': smart_process_id})

    # pprint(s_p)
    print('Получаю юрлицо с нашей стороны')
    c_id = s_p['item']['ufCrm4_1699361952']

    print('Получаю формат договора')
    format_id = s_p['item']['ufCrm4_1696272505025']


    print('ЮЛ с нашей стороны', c_id)

    print('Определяю форму юрлица на стороне клиента')

    client_inn = func.b.call('crm.company.get',  {'id': s_p['item']['companyId']})['UF_CRM_1690987965649']
    print(f'Кол-во символов инн  = {len(client_inn)}')

    if len(client_inn) == 12:
        print('Клиент является физлицом или ип')
        company_type = False
    if len(client_inn) == 10:
        print('клиент является юрлицом')
        company_type = True
    else:
        print('с инн клиента чето не так, проверьте поле инн')



    print('Запускаю поиск шаблона')
    try:
        if company_type:
            template = template_finder(format=str(format_id), company=str(c_id))
            print(template)
        if not company_type:
            template = template_finder_ip(format=str(format_id), company=str(c_id))
            print(template)
    except Exception as e:
        return f'Ошибка при поиске шаблона, по входным данным `[Формат={format_id}, Юл_с_нашей_стороны={c_id}]`, не удалось определить шаблон документа'

    doc = func.b.get_all('crm.documentgenerator.document.add', {
        'templateId': template,
        'entityTypeId': '162',
        'entityId': smart_process_id,
        'values': {
            'title': 'ghdbtn MIR',
            'MY_COMPANY': s_p['item']['ufCrm4_1696252759']
        }
    })
    print(doc.keys())
    # pprint(doc)

    doc_url = doc['document']['downloadUrlMachine']
    doc_title = doc['document']['title']
    response = requests.get(doc_url)

    # Кодируем содержимое файла в формат Base64
    base64_content = base64.b64encode(response.content).decode('utf-8')
    print('тайтл')
    print(doc_title)

    # Пихаем это все в б24 в поле `Договор` -> ufCrm4_1696431440310
    upload = func.b.call('crm.item.update', {
    "entityTypeId": 162,
    "id": int(smart_process_id),
    'fields': {
        'ufCrm4_1696431440310': {
            'data': {
                    'NAME': f'{doc_title}.docx',
                    'fileContent': base64_content,
                    'generateUniqueName': False
                },

        }
    }}, raw=True)

    print(upload)


    sucses = f'''Для карточки дог-ра {smart_process_id}, cоздан документ по шаблону {template}\n
    '''

    return sucses


@app.post('/num_to_text/')
def num_to_text(auth, number, case='родительный'):
    """
    # Возвращает число преобразованное в текст

    Значения для падежей: \n
    ```
        "именительный": 'nomn',
        "родительный": 'gent',
        "дательный": 'datv',
        "винительный": 'accs',
        "творительный": 'ablt',
        "предложный": 'loct'
    ```
    """
    if auth != AUTH:
        print(auth)
        return 'invalid auth_token'


    result = func.sklonenie_chisla(number, case)
    return result


@app.post('/word_to_case/')
def word_to_case(auth, word, case='родительный'):
    """
    # Возвращает слово в определенном падеже

    Значения для падежей: \n
    ```
        "именительный": 'nomn',
        "родительный": 'gent',
        "дательный": 'datv',
        "винительный": 'accs',
        "творительный": 'ablt',
        "предложный": 'loct'
    ```
    """
    if auth != AUTH:
        print(auth)
        return 'invalid auth_token'

    result = func.sklonenie_polnogo_imeni(word, case)
    return result


@app.post('/check_contract/')
def check_contract(auth, contract_id):
    if auth != AUTH:
        print(auth)
        return 'invalid auth_token'


    contract_fields_to_check = [
        'UF_CRM_4_1696272505025', # Формат договора
        'UF_CRM_4_1696266393755', # Максимальная сумма кредита
        'UF_CRM_4_1697045531854', # Срок отсрочки платежа
    ]
    company_fields_to_check = [
        'UF_CRM_1697650419', # Карточка контрагента
        'UF_CRM_1697650557', # Копия Свидетельства о внесении записи в ЕГРЮЛ/ЕГРИП
        'UF_CRM_1697650520', # Копия паспорта (страница с фотографией, регистрацией по месту жительства)
        'UF_CRM_1697650580', # Копия Свидетельства о постановке на учет в налоговом органе (ИНН)
        'PHONE', # Телефон
        'EMAIL', # EMAIL
    ]
    company_fields_to_check_ip = [
        'UF_CRM_1705571290', # Паспорт | Серия
        'UF_CRM_1705571304', # Паспорт | Номер
        'UF_CRM_1705571321', # Паспорт | Кем выдан
        'UF_CRM_1705571339', # Паспорт | Код подразделения
        'UF_CRM_1705571394', # Паспорт | Дата выдачи
        'UF_CRM_1705571426', # Паспорт | Адрес регистрации
        # 'ADDRESS_LEGAL',
    ]
    company_fields_to_check_ul = [
        # 'UF_CRM_1706190888846', # Копия бухгалтерского баланса
        'UF_CRM_1697650477', # Копия устава (первая, последняя страницы и страница с полномочиями руководителя)
        'UF_CRM_1697650459', # Копия решения о назначении руководителя или копия приказа о назначении руководителя
        'UF_CRM_1697650419', # Карточка контрагента
        'UF_CRM_1697650557', # Копия Свидетельства о внесении записи в ЕГРЮЛ/ЕГРИП
        # 'UF_CRM_1711313588', # Копия паспорта (страница с фотографией, регистрацией по месту жительства)
        'UF_CRM_1697650580', # Копия Свидетельства о постановке на учет в налоговом органе (ИНН)
        'PHONE', # Телефон
        'EMAIL', # EMAIL
    ]
    rq_fields_to_check_ip = {
        'RQ_INN': 'ИНН', # ИНН
        'RQ_COMPANY_NAME': 'Сокращенное наименование организации', # Сокращенное наименование организации
        'RQ_COMPANY_FULL_NAME': 'Полное наименование организации', # Полное наименование организации
        'RQ_LAST_NAME': 'Фамилия', # Фамилия
        'RQ_FIRST_NAME': 'Имя', # Имя
        'RQ_SECOND_NAME': 'Отчество', # Отчество
        'RQ_OGRNIP': 'ОГРНИП', # ОГРНИП
    }
    rq_fields_to_check_ul = {
        'RQ_INN': 'ИНН', # ИНН
        'RQ_COMPANY_NAME': 'Сокращенное наименование организации', # Сокращенное наименование организации
        'RQ_COMPANY_FULL_NAME': 'Полное наименование организации', # Полное наименование организации
        'RQ_OGRN': 'ОГРН', # ОГРН
        'RQ_KPP': 'КПП', # КПП
        'RQ_DIRECTOR': 'Генеральный директор', # Генеральный директор
    }
    bank_rq_fields_to_check = {
        'RQ_BANK_NAME' : 'Наименование банка',
        'RQ_BIK': "БИК",
        'RQ_ACC_NUM': "Расчетный счёт",
        'RQ_COR_ACC_NUM': "Кор. счёт",
    }
    contract = func.crm_item_get(contract_id)['item']
    company_id = contract['companyId']
    company = func.b.call('crm.company.get', {'id': company_id})
    try:
        rq = func.get_company_rq_list(company_id)
    except:
        rq = False

    check_result = []
    # return contract
    # Провекра карточки договора
    # формат договора == предоплата 100
    if contract['ufCrm4_1696272505025'] == 134:
        ...
    # формат договора == Отсрочка платежа
    if contract['ufCrm4_1696272505025'] == 136:
        if not contract['ufCrm4_1697045531854']:
            check_result.append(f'- Поле "Срок отсрочки платежа" [URL=https://orgtraid.orgtraid.ru/crm/type/162/details/{contract["id"]}/] в карточке договора [/URL] ↵')
    # формат договора == Кредитный лимит + Отсрочка платежа
    if contract['ufCrm4_1696272505025'] == 161:
        if not contract['ufCrm4_1697045531854']:
            check_result.append(f'- Поле "Срок отсрочки платежа" [URL=https://orgtraid.orgtraid.ru/crm/type/162/details/{contract["id"]}/] в карточке договора [/URL] ↵')
        if not contract['ufCrm4_1696266393755']:
            check_result.append(f'- Поле "Сумма кредита по договору" [URL=https://orgtraid.orgtraid.ru/crm/type/162/details/{contract["id"]}/] в карточке договора [/URL] ↵')
    if check_result:
        check_result.insert(0, '⛔️ [B]В карточке договора не заполнены данные в следующих полях:[/B]')
        check_result.append('[B]Заполните в карточке договора требуемые данные в указанных полях[/B]')

    # Проверка карточки компании
    print('Определяю форму юрлица на стороне клиента')

    client_inn = company['UF_CRM_1690987965649']
    print(f'Кол-во символов инн  = {len(client_inn)}')

    check = False
    if len(client_inn) == 12:
        print('Клиент является физлицом или ип')
        # Передаем поля для проверки ип
        # company_fields_to_check = company_fields_to_check.extend(company_fields_to_check_ip)
        for i in company_fields_to_check_ip:
            company_fields_to_check.append(i)
        # check = func.company_field_checker(company, company_fields_to_check_ip)
    if len(client_inn) == 10:
        print('клиент является юрлицом')
        # print(company_fields_to_check)
        # Передаем поля для проверки ЮЛ
        company_fields_to_check = company_fields_to_check_ul

    else:
        print('с инн клиента чето не так, проверьте поле инн')
    print(type(company))
    print(type(company_fields_to_check))
    check = func.company_field_checker(company, company_fields_to_check)
    if check:
        check_result.append('- - -')
        check_result.append('')
        check_result.append('⛔️ [B]В карточке компании не заполнены данные в следующих полях:[/B]')
        check_result.append('')
        # check_result.extend(check)
        check_result.extend(check)
        check_result.append('[B]Заполните в карточке компании требуемые данные в указанных полях[/B]')
    if check_result:
        check_result.append('- - -')
        check_result.append('')

    # Проверка наличия реквизитов карточки компании
    rq_check_result = []
    if not rq:
        rq_check_result.append(f'❌ [B]В карточке клиента не заполнены реквизиты[/B] [URL=https://orgtraid.orgtraid.ru/crm/company/details/{company_id}/] Перейти к компании [/URL] ↵')
        rq_check_result.append(f'Заполните реквизиты клиента')
    try:
        address = func.rq_address_get(rq["ID"])
        print(address)
    except:
        address = {}
    if not address:
        if len(client_inn) == 10:
            rq_check_result.append(f'❌ [B]Поле Юридический адрес не заполнено[/B] [URL=https://orgtraid.orgtraid.ru/crm/company/details/{company_id}/] Перейти к компании [/URL] ↵')
            rq_check_result.append('Заполните поле Юридический адрес')

    print('Получаю банковские реквизиты')
    try:
        bank_rq = func.get_bank_rq_list(rq['ID'])
    except:
        bank_rq = []
        rq_check_result.append(f'❌ [B]Банковские реквизиты клиента не заполнены[/B] [URL=https://orgtraid.orgtraid.ru/crm/company/details/{company_id}/] Перейти к компании [/URL] ↵')
        rq_check_result.append('Заполните банковские реквизиты клиента')
    if rq_check_result:
        check_result.extend(rq_check_result)
        # return check_result

    # Провекра полей реквизитов
    rq_fields_check_result = False
    if rq:
        print('Проверяю реквизиты компании')
        print('')
        print(len(client_inn))
        if len(client_inn) == 12:
            print('Запускаю проверку реквизита для ИП ))')
            rq_fields_check_result = func.rq_checker(company_id, rq, rq_fields_to_check_ip)
        if len(client_inn) == 10:
            print('Запускаю проверку реквизита для Юрлиц ))')
            rq_fields_check_result = func.rq_checker(company_id, rq, rq_fields_to_check_ul)

        if rq_fields_check_result:

            check_result.append('- - -')
            check_result.append('')
            check_result.append('⛔️ [B]В реквизитах клиента не заполнены данные в следующих полях:[/B]')
            for i in rq_fields_check_result:
                check_result.append(i)
            check_result.append('[B]Заполните в реквизитах клиента требуемые данные в указанных полях[/B]')

    if bank_rq:
        bank_rq_check = []
        print('Проверяю банковский реквизит')
        for i in bank_rq_fields_to_check:
            print(i)
            if not bank_rq[i]:
                bank_rq_check.append(f'- Поле {bank_rq_fields_to_check[i]} в банковском реквизите [URL=https://orgtraid.orgtraid.ru/crm/company/details/{company_id}/] Перейти к компании [/URL] ↵')

        if bank_rq_check:
            check_result.append('- - -')
            check_result.append('')
            check_result.append('⛔️ [B]Банковские реквизиты клиента не заполнены в следующих полях:[/B]')
            check_result.extend(bank_rq_check)
            check_result.append('[B]Заполните банковские реквизиты клиента в указанных полях[/B]')

    return check_result

