#!/usr/bin/env python
import os
import secrets

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coolweb.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def run():
    sups = list(User.objects.filter(is_superuser=True).values_list('username', flat=True))
    print('Existing superusers:', sups)
    if sups:
        u = User.objects.get(username=sups[0])
        pw = secrets.token_urlsafe(12)
        u.set_password(pw)
        u.save()
        print('Updated superuser:', u.username)
        print('New password:', pw)
    else:
        base = 'admin'
        i = 1
        uname = base
        while User.objects.filter(username=uname).exists():
            i += 1
            uname = f'{base}{i}'
        pw = secrets.token_urlsafe(12)
        email = f'{uname}@example.com'
        u = User.objects.create_user(uname, email, pw)
        u.is_superuser = True
        u.is_staff = True
        u.save()
        print('Created superuser:', uname)
        print('Password:', pw)

if __name__ == '__main__':
    run()
