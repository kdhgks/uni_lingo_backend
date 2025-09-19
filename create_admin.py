#!/usr/bin/env python
"""
관리자 계정 생성 스크립트
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'language_exchange.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_admin():
    """관리자 계정 생성"""
    print("=== 관리자 계정 생성 ===")
    
    # 관리자 계정 정보
    admin_email = "admin@unilingo.com"
    admin_password = "admin123"
    admin_nickname = "관리자"
    
    # 기존 관리자 계정 확인
    if User.objects.filter(email=admin_email).exists():
        print(f"관리자 계정이 이미 존재합니다: {admin_email}")
        return
    
    # 관리자 계정 생성
    try:
        admin_user = User.objects.create_user(
            username=admin_email,  # username 필드 추가
            email=admin_email,
            password=admin_password,
            nickname=admin_nickname,
            is_staff=True,
            is_superuser=True
        )
        
        print(f"관리자 계정이 성공적으로 생성되었습니다!")
        print(f"이메일: {admin_email}")
        print(f"비밀번호: {admin_password}")
        print(f"닉네임: {admin_nickname}")
        print(f"관리자 권한: {admin_user.is_staff}")
        print(f"슈퍼유저 권한: {admin_user.is_superuser}")
        
    except Exception as e:
        print(f"관리자 계정 생성 실패: {e}")

if __name__ == "__main__":
    create_admin()
