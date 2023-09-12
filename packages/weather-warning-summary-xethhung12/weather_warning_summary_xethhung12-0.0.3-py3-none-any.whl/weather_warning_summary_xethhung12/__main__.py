import sys

from weather_warning_summary_xethhung12 import get_connection, load_map
import datetime as dt

if __name__ == '__main__':
    path = sys.argv[1]
    print(path)
    conn = get_connection(path)
    time = dt.datetime.now().isoformat()
    m = load_map("https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warnsum&lang=en")
    conn.execute("insert into weather (time, message) values (?, ?)", (time, m))
    conn.commit()
    print(time)
    print(m)
    print("Done")
