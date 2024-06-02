import func
import re

people_dict = {
    "1": 'Равшан Курочкин',
    "2": 'Намаз Гаитов',
    "3": 'Кирья Оцепов',
    "4": 'Муаммар Намасваев',
    "5": 'Боренька Бесстархов',
    "6": 'Настенька Безупрекова',
    "7": 'Феденька Рыцарев',
    "8": 'Рубен Рябушко',
    "9": 'Юлия Равшановски',
    "10": 'Сеня Авсвеетов',
    "11": 'Махмут Реггиночиев',
    "12": 'Патима Побратан-Междуногова',
}

company_dict = {
    "171": 'ООО "ТРЕЙД-РЕСУРС"',
    "172": 'ООО "ПРОМОСПЕКТР"'
}

formats = {
    '134': '-предоплата-юрлицо',
    '161': '-лимит+отсрочка-юрлицо',
    '136': '-отсрочка-юрлицо',
}

formats_ip = {
    '134': '-предоплата-ИП',
    '161': '-лимит+отсрочка-ИП',
    '136': '-отсрочка-ИП',

}

templates_base = {
    "63": "7.ПАРТНЕР-лимит+отсрочка-юрлицо",
    "66": "4.ПРАЙМ ПАРТС-лимит+отсрочка-юрлицо"
}


template_base_ip = {
    '130': '5.ОПТТРЕЙД-предоплата-ИП',
    '131': '6.ПАРТНЕР-предоплата-ИП'
}


# seen = set()
# duplicates = set(x for x in data_dict.values() if x in seen or seen.add(x))

# print("Duplicate values:", duplicates)

def template_finder(format, company):
    company_name = re.search(r'"([^"]*)"', company_dict[company]).group(1)
    key = f"{company_name}{formats[format]}"
    print('ищю ключ', f"{company_name}{formats[format]}")
    for i in templates_base:
        if key in templates_base[i]:
            return i
    return(f'Не удалось найти шаблон по комбинации {key}')

def template_finder_ip(format, company):
    company_name = re.search(r'"([^"]*)"', company_dict[company]).group(1)
    key = f"{company_name}{formats_ip[format]}"
    print('ищю ключ', f"{company_name}{formats_ip[format]}")
    for i in template_base_ip:
        if key in template_base_ip[i]:
            return i
    return(f'Не удалось найти шаблон по комбинации {key}')


