'''
django admin pages for UserPreference models
'''

from user_api.models import UserPreference
from ratelimitbackend import admin

admin.site.register(UserPreference)