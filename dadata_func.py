from dadata import Dadata

from pprint import pprint

import keys

token = keys.DADATA_TOKEN
secret = keys.DADATA_SECRET

def req_finder(inn):
    with Dadata(token, secret) as dadata:
        # Ищем среди юрлиц
        result = dadata.find_by_id(
            name="party",
            query=inn,
            type='LEGAL'
        )
        # Если пусто, ищем среди ИП
        if not result:
            result = dadata.find_by_id(
                name="party", 
                query=inn,
                type='INDIVIDUAL'
            )    
    if not result:
        return None
    # print(type(result))
    return result[0]['data']



