#!/usr/bin/env python
import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'language_exchange.settings')
django.setup()

from users.models import User, UserLanguage

# 모든 사용자 조회
users = User.objects.all()
print(f'총 사용자 수: {users.count()}')

for user in users[:5]:  # 처음 5명만 확인
    teaching_langs = list(user.languages.filter(language_type='teaching').values_list('language', flat=True))
    learning_langs = list(user.languages.filter(language_type='learning').values_list('language', flat=True))
    print(f'사용자 {user.email}:')
    print(f'  - 가르치는 언어: {teaching_langs}')
    print(f'  - 배우는 언어: {learning_langs}')
    print()

