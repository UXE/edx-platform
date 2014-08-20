'''
django admin pages for courseware model
'''

from student.models import UserProfile, UserTestGroup, CourseEnrollmentAllowed, MigratedUser
from student.models import CourseEnrollment, Registration, PendingNameChange
from ratelimitbackend import admin

admin.site.register(UserProfile)

admin.site.register(MigratedUser)

admin.site.register(UserTestGroup)

admin.site.register(CourseEnrollment)

admin.site.register(CourseEnrollmentAllowed)

admin.site.register(Registration)

admin.site.register(PendingNameChange)
