import numpy as np
from datetime import timezone

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

def datetime_to_local(utc_datetime):
    offset = utc_datetime.replace(tzinfo=timezone.utc) - utc_datetime.astimezone(timezone.utc)
    return utc_datetime + offset
