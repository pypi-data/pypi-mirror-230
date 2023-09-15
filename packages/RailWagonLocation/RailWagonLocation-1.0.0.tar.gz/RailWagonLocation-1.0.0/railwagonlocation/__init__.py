import httpx

class RailWagonLocation:
    
    base_url = None
    username = None
    password = None
    return_formats = [
        "xml",
        "xmlZipped",
        "json",
        "jsonZipped"
    ]
    
    def __init__(self, username: str, password: str, base_url: str, return_format : str ="json"):
        if return_format not in self.return_formats:
            raise ValueError("return_format must be one of {}".format(self.return_formats))
        if not username:
            raise ValueError("username is required")
        if not password:
            raise ValueError("password is required")
        if not base_url:
            raise ValueError("base_url is required")
        self.username = username
        self.password = password
        self.return_format = return_format
        self.base_url = base_url
        self.client = httpx.Client(http2=True)
        pass
    
    def make_request(self, **args):
        args["name"] = self.username
        args["password"] = self.password
        args["return_format"] = self.return_format
        response = self.client.get(self.base_url, params=args)
        return response.json() if self.return_format == "json" else r.text
        
    
    def get_wagon_info(self, vagon_number: str):
        """Получение данных о конкретном вагоне, стоящем на слежении

        Аргументы:
            vagon_number (str): Номер вагона

        Возвращает:
            Объект: Полная информация о вагоне
        """
        return self.make_request(request_type="view_vagon",vagon_no=vagon_number)
    
    def get_wagon_repair_history(self, vagon_number: str):
        """Получение истории ремонтов конкретного вагона по номеру вагона

        Аргументы:
            vagon_number (str): Номер вагона

        Возвращает:
            Cписок: Cписок ремонтов, произведённых с вагоном
        """
        return self.make_request(request_type="view_vagon_repairs",vagon_no=vagon_number)
    
    def get_wagon_history(self, vagon_number: str, days_limit: int = 30):
        """Получение истории передвижения конкретного вагона

        Аргументы:
            vagon_number (str): Номер вагона
            days_limit (int, optional): Количество дней, за которые получить историю. Значение по умолчанию – 30.

        Возвращает:
            Cписок: Cписок истории передвижения вагона
        """
        return self.make_request(request_type="view_vagon_history",vagon_no=vagon_number,days_limit=days_limit)
    
    def get_all_wagons_info(self, all_operations=False, added_last_minutes="60", calendar_date=None):
        """Получение данных о всех вагонах пользователя

        Аргументы:
            all_operations (str, optional): Показывать все последние операции по каждому вагону или нет. Возможные значения: y – все операции, n – только самую последнюю операцию. Значение по умолчанию – n.
            added_last_minutes (str, optional): Опционально можно указать за какой период выгружать операции (в этом примере за последние 60 минут). Имеет смысл только с параметром all_operations=y
            calendar_date (_type_, optional): дата, за которую даются данные о дислокации. Опционально, по умолчанию берутся самые свежие данные.

        Возвращает:
            Объект: Вагоны пользователя
        """
        all_operations = "y" if all_operations else "n"
        if calendar_date:
            return self.make_request(request_type="get_user_vagons",all_operations=all_operations,calendar_date=calendar_date)
        return self.make_request(request_type="get_user_vagons",all_operations=all_operations,added_last_minutes=added_last_minutes)
    
    def get_inquiries(self, period_start, period_end):
        """Получение справок

        Аргументы:
            period_start (str): Начало периода в формате YYYY-MM-DD
            period_end (str): Конец периода в формате YYYY-MM-DD

        Возвращает:
            Cписок: Cписок справок
        """
        return self.make_request(request_type="get_inquiries",period_start=period_start,period_end=period_end)