import datetime
import json
import os
import requests

MONITOR_URL = os.environ['MONITOR_URL']
MONITOR_KEY = os.environ['MONITOR_KEY']
MONITOR_PROCESS_ID = os.environ['MONITOR_PROCESS_ID']
MONITOR_LOG_PATH = os.environ['MONITOR_LOG_PATH']


class Monitor:
    N_DAYS_LOG_ERROR = 30
    N_DAYS_LOG_INFO = 5

    def __init__(self):
        self._init_time = datetime.datetime.now()
        self._url_monitor = MONITOR_URL
        self._path = MONITOR_LOG_PATH
        # Si no existeix la carpeta logs, la creem
        if not os.path.exists(path=MONITOR_LOG_PATH):
            os.makedirs(MONITOR_LOG_PATH)
        # Netegem els logs que tinguem fins a la data per no carregar el servidor.
        for filename in os.listdir(MONITOR_LOG_PATH):
            f = os.path.join(MONITOR_LOG_PATH, filename)
            if os.path.isfile(f):
                _tip = filename[0:1]
                if _tip not in ['e', 'i']:
                    continue
                _year = int(filename[2:6])
                _month = int(filename[6:8])
                _day = int(filename[8:10])
                _log_date = datetime.date(year=_year, month=_month, day=_day)
                if _tip == 'e' and _log_date < datetime.date.today() - datetime.timedelta(days=self.N_DAYS_LOG_ERROR):
                    os.remove(os.path.join(MONITOR_LOG_PATH, filename))
                if _tip == 'i' and _log_date < datetime.date.today() - datetime.timedelta(days=self.N_DAYS_LOG_INFO):
                    os.remove(os.path.join(MONITOR_LOG_PATH, filename))
        _date = datetime.date.today()
        self._file_name = str(_date.year * 10000 + _date.month * 100 + _date.day) + '.txt'
        self._event_id = None
        self._event_with_errors = False
        try:
            self.info(
                "Informem al servidor de monitorització que iniciem un nou event pel procés " + str(MONITOR_PROCESS_ID))
            r = requests.post(
                url=self._url_monitor + "/events",
                data=json.dumps(
                    {
                        "process_id": MONITOR_PROCESS_ID
                    }),
                headers={
                    "x-access-token": MONITOR_KEY,
                    "Content-Type": "application/json"
                },
                verify=False
            )
            self._event_id = r.json()['id']
            self.info("Comunicació correcte amb el servidor de monitorització. Event iniciat " + str(self._event_id))
        except Exception as e:
            self._log(is_error=True, text='No es pot connectar al servidor de monitorització: ' + str(e))
            self._event_id = None
            self._event_with_errors = True

    def _log(self, is_error: bool, text: str):
        if is_error is True:
            _file_name = 'e_'
        else:
            _file_name = 'i_'
        _file_name += self._file_name
        with open(self._path + "/" + _file_name, "a") as f:
            _time = datetime.datetime.now()
            f.write(str(_time.hour * 10000 + _time.minute * 100 + _time.second).zfill(6) + ": " + text + "\n")

    def info(self, txt: str):
        self._log(is_error=False, text=txt)
        print(txt)
        return

    def error(self, txt: str):
        self._log(is_error=True, text=txt)
        self._event_with_errors = True
        print(txt)
        return

    def close(self):
        if self._event_id is not None:
            try:
                _status = "ok"
                if self._event_with_errors is True:
                    _status = "error"
                r = requests.patch(
                    url=self._url_monitor + "/events/" + str(self._event_id),
                    data=json.dumps(
                        {
                            "status": _status
                        }),
                    headers={
                        "x-access-token": MONITOR_KEY,
                        "Content-Type": "application/json"
                    },
                    verify=False
                )
                if r.status_code not in (200, 201):
                    raise Exception("Http response: " + str(r.status_code))
            except Exception as e:
                self._log(is_error=True, text="No es pot tancar l'event al servidor de monitorització: " + str(e))
            else:
                self.info("Informat al servidor de montirització que s'ha acabat l'event " + str(self._event_id))
