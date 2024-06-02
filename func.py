from fast_bitrix24 import Bitrix
import base64
from pprint import pprint
import keys
from datetime import datetime
import dadata_func
from num2words import num2words
import pymorphy2



import requests



# замените на ваш вебхук для доступа к Bitrix24
webhook = keys.B24_KEY
b = Bitrix(webhook)


def crm_element_add(sp_id, massiv):
    element = b.call('crm.item.add', {
        'entityTypeId': sp_id,
        'fields': massiv
        })
    return element


def crm_item_fields(item_id):
    f = b.get_all('crm.item.fields', {"entityTypeId": item_id})
    return f

def crm_item_get(item_id):
    f = b.get_all('crm.item.get', {'entityTypeId': '162', 'id': item_id})
    return f



def get_sp_field_names(item_id):
    f = b.get_all('crm.item.fields', {"entityTypeId": item_id})
    fields = f['fields']
    fields_dict = {}
    # pprint(fields)
    for field in fields:
        if fields[field]['type'] == 'enumeration':
            list_values = fields[field]['items']
            items = []
            for val in list_values:
                items.append({val['ID']: val['VALUE']})
            fields_dict[field] = [fields[field]['title'], items]
        else: 
            fields_dict[field] = fields[field]['title']
    return fields_dict


def read_file_as_base64(file_path):
    with open(file_path, 'rb') as file:
        file_data = file.read()
        if file_data:
            file_base64 = base64.b64encode(file_data).decode('utf-8')
            return file_base64
        else:
            print("Файл пуст.")
            return None


def crm_item_add(massiv):
    item = b.get_all('crm.item.add', 
    {
        'entityTypeId': '162',
        'fields': massiv
    })
    print(type(item))
    print(item)
    return item

def crm_company_update(c_id, fields:dict):
    c = b.call('crm.company.update', {
        'id': c_id,
        'fields': fields
    })
    return c



def upload_file(file_in_base64, file_name, folder_id):
    upload = b.call(
        'disk.folder.uploadfile',
        {
            'id': folder_id,
            'data': {'NAME': file_name},
            'fileContent': file_in_base64,
            'generateUniqueName': False
        }
    )
    return upload


def crm_source_list():
    source_list = {}
    status_fields = crm_status_fields()
    for i in status_fields:
        if i['ENTITY_ID'] == 'SOURCE':
           key = i['STATUS_ID']
           val = i['NAME']
           source_list[key] = val
    return source_list


'''file_base64 = read_file_as_base64('Вложение.txt')
upload = upload_file(file_base64, 'Вложение.txt', '173064')
print(upload)'''


def get_current_datetime():
    now = datetime.now()
    return str(now.strftime("%d.%m.%Y  %H %M"))

def addsubfolder(parent_id, folder_name):
    folder = b.call('disk.folder.addsubfolder', {
        'id': parent_id,
        'data': {
            'NAME': folder_name
        }
    })
    return folder


def user_search_by_last_name(user_last_name, user_name=''):
    user = b.call('user.search', {
        'FILTER': {"LAST_NAME": user_last_name, 'NAME': user_name},
        "ADMIN_MODE": 'True'
        })
    return user
#print(addsubfolder(1827, f'Отчет Контур фокус {get_current_datetime()}'))


def get_company_rq_list(company_id):
    try:
        rq = b.call('crm.requisite.list', {'filter': {'ENTITY_ID': company_id, 'ENTITY_TYPE_ID':'4'}})
    except:
        rq = []
    return rq


def kill_company_rq(company_id):
    """убивает реквизиты компании"""
    rq = b.get_all('crm.requisite.list', {'filter': {'ENTITY_ID': company_id, 'ENTITY_TYPE_ID':'4'}})
    for i in rq:
        b.call('crm.requisite.delete', {'id': i['ID']})


def get_bank_rq_list(main_rq_id):
    """Получает банковский реквизит по id реквизита родителя"""
    banq_rq = b.call('crm.requisite.bankdetail.list', {'filter': {'ENTITY_ID': main_rq_id}})
    return banq_rq

def bank_rq_add(req_id, data):
    """Создает банковский реквизит, на вход принимает id реквизита родителя"""
    data['ENTITY_ID'] = req_id
    banq_rq  = b.call('crm.requisite.bankdetail.add', {'fields': data})


def crm_company_get(company_id): 
    c = b.call('crm.company.get', {'id': company_id})
    return c


def crm_timeline_comment_add(entity_id, entity_type, comment):
    b.call('crm.timeline.comment.add', {
        'fields': {
            'ENTITY_ID': entity_id,
            'ENTITY_TYPE': entity_type,
            'COMMENT': comment
        }
    })

def signature(full_name):
    parts = full_name.split()  # Разделяем строку на слова
    # Сохраняем фамилию полностью и формируем инициалы только для имени и отчества
    formatted_name = f"{parts[1]} " + "".join([name[0] + "." for name in parts[2:]])
    return formatted_name


class Requisite:
    # Поля реквизита по которым будет работать валидация
    valid_fields = [
        'RQ_INN',
        'RQ_OGRN',
        'RQ_OGRNIP',
        'RQ_OKPO',
        'RQ_DIRECTOR',
        'RQ_KPP',
        'RQ_FIRST_NAME',
        'RQ_SECOND_NAME',
        'RQ_LAST_NAME',
        'NAME',]

    def __init__(self, company_id):
        self.company_id = company_id
        self.company_data = crm_company_get(self.company_id)
        self.company_inn = self.company_data['UF_CRM_1690987965649']
        self.rq_data = get_company_rq_list(self.company_id)
        if self.rq_data:
            self.rq_id = self.rq_data['ID']
        else:
            self.rq_id = ''
    
    def rq_generate(self):
        """Собирает поля реквизита из дадаты"""
        rq = dadata_func.req_finder(self.company_inn)
        correct_data = rq
        pprint(rq)
        rq_fields = {}
        ip_name_short = ''

        # Обработка для ООО
        if correct_data['type'] == 'LEGAL':
            rq_preset = '1'
            rq_fields = {
                'ENTITY_TYPE_ID': '4',
                'PRESET_ID': rq_preset,
                "NAME": correct_data['name']['full_with_opf'],
                'RQ_INN': correct_data['inn'],
                'RQ_DIRECTOR': correct_data['management']['name'],
                'RQ_OGRN': correct_data['ogrn'],
                'RQ_KPP': correct_data['kpp'],
                'RQ_OKPO': correct_data['okpo'],
                'RQ_COMPANY_NAME': correct_data['name']['short_with_opf'],
                'RQ_COMPANY_FULL_NAME': correct_data['name']['full_with_opf'], 
                'ADDRESS_1': correct_data['address']['data']['source'],
                'CITY': correct_data['address']['data']['source'],
                'POSTAL_CODE': correct_data['address']['data']['postal_code'],
                'COUNTRY': correct_data['address']['data']['country'],
                'RQ_COMPANY_REG_DATE': datetime.utcfromtimestamp(correct_data['state']['registration_date'] / 1000).strftime('%Y-%m-%d'),
                'RQ_OKTMO': correct_data['oktmo']                
            }
        
        # Обработка для ИП
        if correct_data['type'] == 'INDIVIDUAL':
            # pprint(correct_data)
            rq_preset = '2'
            rq_fields = {
                'ENTITY_TYPE_ID': '4',
                'PRESET_ID': rq_preset,
                'RQ_COMPANY_NAME': correct_data['name']['short_with_opf'],
                'RQ_COMPANY_FULL_NAME': correct_data['name']['full_with_opf'],
                "NAME": correct_data['name']['full_with_opf'],
                'RQ_INN': correct_data['inn'],
                'RQ_OGRNIP': correct_data['ogrn'],
                'RQ_OKPO': correct_data['okpo'],
                'RQ_OKVED': correct_data['okved'],
                'RQ_KPP': '',
                'ADDRESS_1': '',
                'CITY': '',
                'POSTAL_CODE': '',
                'COUNTRY': '',
            }
           
            ip_name = correct_data['name']['short_with_opf'].split(' ')
            ip_name_short = signature(correct_data['name']['short_with_opf'])
            rq_fields['RQ_FIRST_NAME'] = ip_name[2]
            rq_fields['RQ_SECOND_NAME'] = ip_name[3]
            rq_fields['RQ_LAST_NAME'] = ip_name[1]
            rq_fields['RQ_NAME_IP_NAME_SHORT'] = ip_name_short
        
        rq_fields['ENTITY_ID'] = self.company_id
        # print(rq_fields)
        return rq_fields

    def rq_diff(self):
        """Сравнивает текущий реквизит с реквизитом из дадаты
        Если реквизит совпадает, отдает True
        Если не совпадает, отдает False и ключ `diffs` с полями, которые расходятся"""
        new_rq_data = self.rq_generate()
        valid_diffs = {field: {'Значение из Битрикс24': self.rq_data[field], 'Значение из Дадаты': new_rq_data.get(field)}
                       for field in self.valid_fields if self.rq_data.get(field) != new_rq_data.get(field)}
        result = {'diffs': valid_diffs, 'match': not bool(valid_diffs)}

        post = '''
        Зафиксированы отклонения в реквизитах:
        '''
        # print(result['diffs'])

        for i in result['diffs']:
            post += f"""
                - {i}
                - В Б24:
                    - {result['diffs'][i]['Значение из Битрикс24']}
                - В DADATA:
                    - {result['diffs'][i]['Значение из Дадаты']}
            """ 
        # print(post)
        if result['diffs']:
            crm_timeline_comment_add(
                entity_id=self.company_id,
                entity_type='company',
                comment=post
                # str(result['diffs'])
            )
        return result


    def rq_update(self):
        """
        Сохраняет новое значение объекта реквизита
        """
        pass
    
    def rq_add(self):
        """
        Заполняет карточку компании значениями полученными из даддаты
            - Краткое наименование, пишет в название компании
            - Адрес из реквизита, пишет в юр. адрес компании
            - Значения реквизита, пишет в реквизит
        """
        
        # Создаем реквизит в битркисе
        new_rq_data = self.rq_generate()
        # return new_rq_data
        bx_requesite = b.call(
            'crm.requisite.add', {
                'fields': new_rq_data
            }
        )
        if not 'RQ_NAME_IP_NAME_SHORT' in new_rq_data.keys():
            new_rq_data['RQ_NAME_IP_NAME_SHORT'] = ''

        # Добавляем адрес к созданому реквизиту
        requisite_address = b.call(
                'crm.address.add', {
                    'fields': {
                        'TYPE_ID': '6',
                        'ENTITY_TYPE_ID': '8',
                        'ENTITY_ID': bx_requesite,
                        'ANCHOR_TYPE_ID': '4',
                        'ANCHOR_ID': self.company_id,
                        'ADDRESS_1': new_rq_data['ADDRESS_1'],
                        'CITY': new_rq_data['CITY'],
                        'POSTAL_CODE': new_rq_data['POSTAL_CODE'],
                        'COUNTRY': new_rq_data['COUNTRY']
                    
                    }
                }
            )
        
        # Обновляем название компании и поле КПП
        crm_company_update(self.company_id, {

            'TITLE': new_rq_data['RQ_COMPANY_NAME'],
            'UF_CRM_1700522340677': new_rq_data['RQ_KPP'],
            'UF_CRM_1705577436353': new_rq_data['RQ_NAME_IP_NAME_SHORT'], 
            })
        return 'Процесс автозаполнения карточки компании завершен. Карточка компании дополнена данными из ФНС'
    
def rq_address_get(rq_id):
    """Возвращает адрес реквизита"""
    try:
        address = b.call('crm.address.list', {'filter': {'ENTITY_ID': rq_id}})
        return address
    except Exception as e:
        return {}

def user_find(email):
    """Ищет пользователя на портале по email"""
    user = b.get_all(
        'user.search', {
            'FILTER': {
                'EMAIL': email,
                'USER_TYPE': ['extranet', 'employee']
                # 'USER_TYPE': 'extranet'
            }
        }
    )
    return user
    if user: 
        for us in user:
            user = us
        return user
    else:
        return f'На портале нет пользователя с почтой {email}'


def user_struct_update(user_id, name, last_name, second_name, department_id, WORK_POSITION):
    """Обновляет фио и отдел пользователя"""
    usr_updt = b.call('user.update', {
                'ID': user_id,
                'NAME': name,
                'LAST_NAME': last_name,
                'SECOND_NAME': second_name,
                'UF_DEPARTMENT': department_id,
                'WORK_POSITION': WORK_POSITION,
                'UF_CHANGED': '1'

            })
    response = requests.post(url='https://orgtraid.orgtraid.ru/local/php/change_user.php', data={'id': user_id, 'status': 1})
    return usr_updt


def sklonenie_chisla(number, case):
    # Словарь с падежами для pymorphy2
    cases = {
        "именительный": 'nomn',
        "родительный": 'gent',
        "дательный": 'datv',
        "винительный": 'accs',
        "творительный": 'ablt',
        "предложный": 'loct'
    }
    
    # Преобразование числа в словесное представление на русском языке
    text_number = num2words(number, lang='ru')
    
    morph = pymorphy2.MorphAnalyzer()
    words = text_number.split()
    # Склонение каждого слова в предложении
    declined_words = []
    for word in words:
        parsed_word = morph.parse(word)[0]
        declined_word = parsed_word.inflect({cases[case]})
        if declined_word:
            declined_words.append(declined_word.word)
        else:
            declined_words.append(word)

    return ' '.join(declined_words)


def sklonenie_polnogo_imeni(full_name, case):
    # Словарь с падежами для pymorphy2
    cases = {
        "именительный": 'nomn',
        "родительный": 'gent',
        "дательный": 'datv',
        "винительный": 'accs',
        "творительный": 'ablt',
        "предложный": 'loct'
    }

    morph = pymorphy2.MorphAnalyzer()
    result = []

    # Разбиваем полное имя на части и склоняем каждую часть
    for part in full_name.split():
        parsed_part = morph.parse(part)[0]
        declined_part = parsed_part.inflect({cases[case]})
        if declined_part:
            result.append(declined_part.word)
        else:
            result.append(part)

    return ' '.join(result)


def get_company_feld_name_by_id(field_id):
    "Отдает название поля компании по идентификатору"
    fields = b.get_all('crm.company.fields')
    if fields[field_id]['title'] == field_id: 
        return fields[field_id]['listLabel']
    return fields[field_id]['title']


def company_field_checker(object, fields_to_check):
    """Проверяет поля на предмет заполненности, если не заполнено:
        - Одтает строку вида `Название поля` по каждому полю"""
    result = []
    fields = b.get_all('crm.company.fields')
    # pprint(fields_to_check) 

    def field_name(field_name):
        if fields[i]['title'] == i: 
            return fields[i]['listLabel']
        return fields[i]['title']
    
    for i in fields_to_check:
        print(i)
        if not i in object.keys() or not object[i]:
            result.append(f'- Поле "{field_name(i)}" [URL=https://orgtraid.orgtraid.ru/crm/company/details/{object["ID"]}/] в карточке компании [/URL] ↵')
    return result


def rq_checker(company_id, object, fields_to_check):
    """Проверяет реквизит компании"""
    result = []
    for i in fields_to_check:
        # print(f'Проверяю поле ->{i}')
        if not object[i]:
            result.append(f'- Поле {fields_to_check[i]} [URL=https://orgtraid.orgtraid.ru/crm/company/details/{company_id}/] Перейти к компании [/URL] ↵')
    # print(result)
    return result

