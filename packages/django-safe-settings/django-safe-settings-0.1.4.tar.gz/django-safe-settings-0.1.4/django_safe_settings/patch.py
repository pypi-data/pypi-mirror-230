
import inspect

from .settings import DJANGO_SAFE_SETTINGS_CIPHER


def fix_data(data):
    if isinstance(data, dict):
        for key in list(data.keys()):
            data[key] = fix_data(data[key])
    elif isinstance(data, list):
        for index in range(len(data)):
            data[index] = fix_data(data[index])
    elif isinstance(data, str):
        # allow user to add enc: prefix
        if data.startswith("ENC:"):
            data = data[4:]
        if data.startswith("enc:"):
            data = data[4:]
        try:
            new_data = DJANGO_SAFE_SETTINGS_CIPHER.decrypt(data)
            if new_data: # decrypt may fail silent, so if we got empty new data, then use old data...
                return new_data
        except:
            pass
    return data


def patch_all():
    frame = inspect.currentframe()
    globals = frame.f_back.f_globals
    fix_data(globals)
