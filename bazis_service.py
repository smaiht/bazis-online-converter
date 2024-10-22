import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import os
import time

# Импортируем ваш основной скрипт
import main

class BazisConverterService(win32serviceutil.ServiceFramework):
    _svc_name_ = "BazisConverter"
    _svc_display_name_ = "Bazis Converter Service"
    _svc_description_ = "Service for converting Bazis files"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False

    def SvcDoRun(self):
        try:
            # Устанавливаем текущую директорию там, где лежит скрипт
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            
            # Запускаем ваш основной код
            main.main()
            
        except Exception as e:
            servicemanager.LogErrorMsg(str(e))
            
if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(BazisConverterService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(BazisConverterService)