import datetime
import pytz

class Time_zone:
    def __init__(self, timezone_name):
        self.timezone = pytz.timezone(timezone_name)
    
    def get_current_time(self):
        current_time = datetime.datetime.now(self.timezone)
        return current_time
    
    def convert_time(self, source_time, target_timezone_name):
        if source_time.tzinfo is None:
            raise ValueError("source_time must have a timezone")

        target_timezone = pytz.timezone(target_timezone_name)
        target_time = source_time.astimezone(target_timezone)
        return target_time
    
class add_subtract(Time_zone):
    def __init__(self):
        super().__init__('UTC')  # เรียกใช้งาน timezone UTC
    
    def add_hours(self, source_time, hours):
        return source_time + datetime.timedelta(hours=hours)
    
    def subtract_hours(self, source_time, hours):
        return source_time - datetime.timedelta(hours=hours)
    
    def add_minutes(self, source_time, minutes):
        return source_time + datetime.timedelta(minutes=minutes)
    
    def subtract_minutes(self, source_time, minutes):
        return source_time - datetime.timedelta(minutes=minutes)

class calculate(add_subtract):
    def __init__(self):
        super().__init__()
    
    def time_difference(self, time1, time2):
        difference = time1 - time2
        return {
            "years": difference.days // 365,
            "months": difference.days % 365 // 30,
            "days": difference.days % 30,
            "hours": difference.seconds // 3600,
            "minutes": (difference.seconds % 3600) // 60,
            "seconds": difference.seconds % 60,
        }

def get_time_in_timezone(timezone_name):
    target_timezone = pytz.timezone(timezone_name)
    current_time = datetime.datetime.now(target_timezone)
    return current_time
