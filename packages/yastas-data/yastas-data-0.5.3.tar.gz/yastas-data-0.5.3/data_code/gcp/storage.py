import gcsfs
import datetime

def get_last_date(json_gs):
        files = gcsfs.GCSFileSystem().ls(json_gs, encoding='utf-8')
        dates = []
        for file in files:
            date = file.split("/")[-1]
            if date != '':
                dates.append(date)
            
        # print(dates)
        date_objects = [datetime.datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in dates]
        max_date = max(date_objects)
        return max_date