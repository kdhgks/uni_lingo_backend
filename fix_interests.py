#!/usr/bin/env python
"""
관심사 데이터 정리 스크립트
쉼표로 연결된 잘못된 관심사 데이터를 개별 관심사로 분리
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'language_exchange.settings')
django.setup()

from users.models import UserInterest

def fix_interests():
    """잘못 저장된 관심사 데이터를 수정"""
    print("=== 관심사 데이터 정리 시작 ===")
    
    # 쉼표가 포함된 잘못된 관심사 확인
    wrong_interests = UserInterest.objects.filter(interest__contains=',')
    print(f"쉼표가 포함된 관심사 개수: {wrong_interests.count()}")
    
    if wrong_interests.count() == 0:
        print("수정할 데이터가 없습니다.")
        return
    
    # 잘못된 관심사들 출력
    print("\n잘못된 관심사 목록:")
    for interest_obj in wrong_interests:
        print(f"사용자: {interest_obj.user.nickname}, 관심사: {interest_obj.interest}")
    
    # 잘못된 관심사를 개별 관심사로 분리하여 수정
    print("\n수정 중...")
    fixed_count = 0
    
    for interest_obj in wrong_interests:
        # 쉼표로 분리
        individual_interests = [i.strip() for i in interest_obj.interest.split(',') if i.strip()]
        
        if len(individual_interests) > 1:  # 실제로 분리할 수 있는 경우만
            # 기존 잘못된 관심사 삭제
            interest_obj.delete()
            
            # 개별 관심사로 다시 생성
            for individual_interest in individual_interests:
                UserInterest.objects.create(
                    user=interest_obj.user,
                    interest=individual_interest
                )
            
            print(f"수정 완료: {interest_obj.user.nickname} - {individual_interests}")
            fixed_count += 1
    
    print(f"\n=== 수정 완료 ===")
    print(f"수정된 사용자 수: {fixed_count}")
    print(f"수정 후 쉼표 포함 관심사 개수: {UserInterest.objects.filter(interest__contains=',').count()}")

if __name__ == "__main__":
    fix_interests()

