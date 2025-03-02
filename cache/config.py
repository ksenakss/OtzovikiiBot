from decouple import config

admins = [int(admin_id) for admin_id in config('ADMINS').split(',')]