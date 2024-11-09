from Errors import Error_count_of_list, Too_late, Error_year, Error_month, Error_day, Error_hour, Error_minute, Error_seconds
import datetime

class Checking:
    @staticmethod
    def check_time(time_notification):
        try:
            if len(time_notification) != 6:
                raise Error_count_of_list
            time_notification = list(map(int, time_notification))
            if time_notification[0] < datetime.datetime.now().year:
                raise Error_year
            if time_notification[1] not in range(1,12+1):
                raise Error_month
            if time_notification[2] not in range(1,31+1):
                raise Error_day
            if time_notification[3] not in range(0,23+1):
                raise Error_hour
            if time_notification[4] not in range(0,59+1):
                raise Error_minute
            if time_notification[5] not in range(0,59+1):
                raise Error_seconds
            that_time = datetime.datetime(time_notification[0], time_notification[1], time_notification[2], time_notification[3], time_notification[4], time_notification[5])
            current_time = datetime.datetime.now()
            if that_time < current_time:
                raise Too_late
        except Error_count_of_list as error:
            return error
        except ValueError as error:
            return error
        except Too_late as error:
            return error
        except Error_year as error:
            return error
        except Error_month as error:
            return error
        except Error_day as error:
            return error
        except Error_hour as error:
            return error
        except Error_minute as error:
            return error
        except Error_seconds as error:
            return error
        else:
            error = None
            return error



