import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import time
import os
from datetime import datetime

class DesktopService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DesktopEnabler"
    _svc_display_name_ = "Desktop Enabler Service"
    _svc_description_ = "Enables desktop interaction for background processes"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        try:
            # Создадим файл для логов рядом со скриптом
            log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'desktop_service.log')
            
            while self.running:
                # Просто пишем в лог что служба работает
                with open(log_path, 'a') as f:
                    f.write(f"{datetime.now()} - Desktop service is running\n")
                
                # Спим 60 секунд
                time.sleep(60)

        except Exception as e:
            # Если что-то пошло не так, записываем ошибку
            with open(log_path, 'a') as f:
                f.write(f"{datetime.now()} - Error: {str(e)}\n")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DesktopService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(DesktopService)