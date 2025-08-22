class Udr:
    def __init__(self,data):
        self.data = data

class UdrData:
    def __init__(self,report_header,report_row,message,status):
        self.report_header = report_header
        self.report_row = report_row
        self.message = message
        self.status = status

class UdrReportHeader:
    def __init__(self,header):
        self.header = header #LISTA DINAMICA DE LAS CABECERAS DEL REPORTE

class UdrReportRow:
    def __init__(self,reportRow):
        self.reportRow = reportRow # LISTA DINAMICA DE LOS ELEMENTOS DEL REPORTE