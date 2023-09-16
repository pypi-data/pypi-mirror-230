import datetime
import pytz, math

limit_minutes_per_slot = 10

start_time = datetime.datetime(2023, 6, 14, 12, 59, tzinfo=pytz.UTC)


next_minutes = start_time.minute + limit_minutes_per_slot - (start_time.minute % limit_minutes_per_slot)
# Floor math of next_mintutes / 60
print("next_minutes before", next_minutes)

next_minutes_carries_int = math.floor(next_minutes / 60)
print("carries", next_minutes_carries_int)
next_minutes %= 60

# next_minutes = 1  # Example value
# next_minutes_carries_int = 1  # Example value

next_tenth_minutes = datetime.datetime(
    start_time.year, start_time.month, start_time.day,
    start_time.hour, next_minutes,
    tzinfo=pytz.UTC
)

# Add the minute in datetime as delta if the minute carries
if next_minutes_carries_int > 0:
    minutes_to_add = datetime.timedelta(hours=next_minutes_carries_int)
    next_tenth_minutes += minutes_to_add

print("start_time:", start_time)
print("next_tenth_minutes:", next_tenth_minutes)
print("minutes_to_add:", minutes_to_add)
