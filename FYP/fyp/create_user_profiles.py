from django.contrib.auth.models import User
from PerfectParking.models import UserProfile

for user in User.objects.all():
    if not hasattr(user, 'profile'):
        UserProfile.objects.create(user=user)