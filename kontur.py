import requests
import base64
import os
import cgi
import keys
from pprint import pprint


def get_pdf_title(response):
    # Если заголовок 'Content-Disposition' присутствует в ответе, получим название из него
    content_disposition = response.headers.get('Content-Disposition')
    if content_disposition:
        _, params = cgi.parse_header(content_disposition)
        filename = params.get('filename')
        if filename:
            return filename

    # В противном случае, создадим название файла на основе URL
    url_path = response.url.split('?')[0]
    return os.path.basename(url_path)


def download_pdf_express(url, title):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        pdf_content = b""
        for chunk in response.iter_content(chunk_size=8192):
            pdf_content += chunk

        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        
        result_dict = {
            "base64_file": pdf_base64,
            "title": title
        }

        return result_dict
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


# def get_concurrent_bank_stages(inn: str):
#     url = f"https://focus-api.kontur.ru/api3/companyBankruptcy?inn={inn}&key={keys.KONTUR_KEY}"
#     response = requests.get(url)
    
#     if response.status_code == 200:
#         response_data = response.json()
#         stages = [item.get('stage') for item in response_data]
#         return stages
#     else:
#         return []


# def get_fssp_data(inn: str): # - испольнительные произ-ва | нет инн для теста
#     url = f"https://focus-api.kontur.ru/api3/fssp?inn={inn}&key={keys.KONTUR_KEY}"
#     response = requests.get(url)
    
#     if response.status_code == 200:
#         response_data = response.json()
#         for i in response_data:
#             fssp_list = i.get("Исполнительные производства - fssp", [])
#             return fssp_list
#     else:
#         return []


# def get_organization_status(inn: str):
#     url = f"https://focus-api.kontur.ru/api3/req?inn={inn}&key={keys.KONTUR_KEY}"
#     response = requests.get(url)
    
#     if response.status_code == 200:
#         response_data = response.json()
#         status_info = response_data[0]
#         status = status_info['UL']['status']['statusString']
#         return status
#     else:
#         return 'None'


def get_concurrent_bank_stages(inn: str):
    url = f"https://focus-api.kontur.ru/api3/companyBankruptcy?inn={inn}&key={keys.KONTUR_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        response_data = response.json()
        stages = [item.get('stage') for item in response_data]
        if not stages[0]:
            return 'None'
        return stages[0] if stages else 'None'
    else:
        return 'None'


def get_fssp_data(inn: str):
    url = f"https://focus-api.kontur.ru/api3/fssp?inn={inn}&key={keys.KONTUR_KEY}"
    response = requests.get(url)
    result = ''
    
    if response.status_code == 200:
        response_data = response.json()
        for i in response_data:
            fssp_list = i.get("Исполнительные производства - fssp", [])
            result = fssp_list[0] if fssp_list else 'None'
    else:
        result = 'None'
    if result == "None": # is None:
        return 'None'
    else:
        return str(result)


def get_organization_status(inn: str):
    url = f"https://focus-api.kontur.ru/api3/req?inn={inn}&key={keys.KONTUR_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        response_data = response.json()
        #print(response_data)
        status_info = response_data[0]

        status = status_info['UL']['status']['statusString']
        if status: 
            return status
        else:
            return 'None'

    else:
        return 'None'


def get_analytics(inn: str):
    url = f'https://focus-api.kontur.ru/api3/analytics?inn={inn}&key={keys.KONTUR_KEY}'
    response = requests.get(url)
    
    if response.status_code == 200:
        response_data = response.json()
        for i in response_data:
            return i['analytics']
        return response_data

