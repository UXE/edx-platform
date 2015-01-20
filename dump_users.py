from manager import unicodecsv as csv
from django.contrib.auth.models import User


def dump_all_users():
    """
    download all users data needed to migrate them
    """
    users = User.objects.all()
    with open('names.csv', 'w') as csvfile:
    	field_names = ['username', 'email', 'password', 'is_active', 'is_staff', 'is_superuser', 'name', 'level_of_education', 'gender', 'mailing_address', 'city', 'country', 'goals', 'year_of_birth']
	    writer = csv.DictWriter(csvfile, fieldnames=field_names)
	    for user in users:
	        writer.writerow({'username': user.username, 'email': user.email, 'password': user.password, 'is_active': user.is_active, 'is_staff': user.is_staff, 'is_superuser': user.is_superuser, 'name': user.profile.name, 'level_of_education': user.profile.level_of_education, 'gender': user.profile.gender, 'mailing_address': user.profile.mailing_address, 'city': user.profile.city, 'country':user.profile.country, 'goals': user.profile.goals, 'year_of_birth': user.profile.year_of_birth})

	return writer