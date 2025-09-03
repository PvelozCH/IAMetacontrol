import requests
import os


class uniController:
    def getTokenUnifier():
        token = ""
        data = ""
        url = os.getenv("tokenUrlUNIFIER")
        username = os.getenv("UserUNIFIER")
        password = os.getenv("PasswordUNIFIER")

        response = requests.get(url, auth=(username,password))

        if response.status_code == 200:
            data = response.json()
            token = data['token']
        else:
            print("ERROR",response.status_code,response.text)
        
        return token
    # Carga reporte y devuelve el json
    def loadReportUnifier(token,nomReporte):
        data =""
        report_header =""
        report_row = ""
        url = os.getenv("udrUrlUNIFIER")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "reportname":nomReporte
        }
        response = requests.post(url,json=payload,headers=headers)

        if response.status_code == 200:
            # Json que contiene la data completa
            data = response.json()
            # Json que contiene solo las cabeceras
            report_header = response.json()['data'][0]['report_header']
            # Json que contiene los datosdel reporte
            report_row = response.json()['data'][0]['report_row']
        else:
            print("ERROR",response.status_code,response.text)
        
        return data
    
    def fetchBPrecordList(token):
        data =""
        bpname = os.getenv("nomBpnameUNIFIER")
        process = "ADM-0067"
        url = os.getenv("bpFetchUNIFIER",process)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "bpname":bpname,
            "lineitem":"yes"
        }
        response = requests.post(url,json=payload,headers=headers)

        if response.status_code == 200:
            # Json que contiene la data completa
            data = response.json()
        else:
            print("ERROR",response.status_code,response.text)
        
        return data
    
    def getShell(token):
        data =""
        a = {
            "filter":{
                "shell_type":"Project"
            }
        }
        opc = "options:",a
        url = os.getenv("shellUNIFIER",opc)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url,headers=headers)

        if response.status_code == 200:
            # Json que contiene la data completa
            data = response.json()
        else:
            print("ERROR",response.status_code,response.text)
        
        return data
    