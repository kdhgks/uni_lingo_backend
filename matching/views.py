from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import MatchingRequest, MatchingPreference
from .serializers import (
    PartnerSerializer, MatchingRequestSerializer, 
    MatchingStatusSerializer, MatchingSimulateSerializer,
    AdminMatchingRequestSerializer
)
import random

User = get_user_model()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_partners(request):
    """파트너 목록 조회 API"""
    user = request.user
    
    # 기본적으로 모든 사용자를 반환 (자신 제외)
    queryset = User.objects.exclude(id=user.id)
    
    # 현재 사용자의 매칭 요청이 있는지 확인
    try:
        current_request = MatchingRequest.objects.get(user=user, status='pending')
        preferences = current_request.preferences
        
        # 성별 필터링
        if current_request.gender_preference != 'any':
            queryset = queryset.filter(gender=current_request.gender_preference)
        
        # 대학교 필터링
        if current_request.university_preference:
            if current_request.university_preference == 'same_university':
                queryset = queryset.filter(university=user.university)
            elif current_request.university_preference == 'specific_university':
                if current_request.specific_university:
                    queryset = queryset.filter(school=current_request.specific_university)
            else:
                queryset = queryset.filter(university=current_request.university_preference)
        
        # 언어 매칭 필터링 (가르치고 싶은 언어와 배우고 싶은 언어가 일치하는 사용자)
        if preferences.teaching_languages and preferences.learning_languages:
            teaching_languages = preferences.teaching_languages
            learning_languages = preferences.learning_languages
            
            # 가르치고 싶은 언어를 배우고 싶어하는 사용자들
            teaching_matches = Q()
            for lang in teaching_languages:
                teaching_matches |= Q(languages__language=lang, languages__language_type='learning')
            
            # 배우고 싶은 언어를 가르칠 수 있는 사용자들
            learning_matches = Q()
            for lang in learning_languages:
                learning_matches |= Q(languages__language=lang, languages__language_type='teaching')
            
            queryset = queryset.filter(teaching_matches & learning_matches)
            
    except MatchingRequest.DoesNotExist:
        # 매칭 요청이 없으면 필터링 없이 모든 사용자 반환
        pass
    
    # 랜덤하게 섞기
    partners = list(queryset.distinct())
    random.shuffle(partners)
    
    # 최대 20명까지만 반환
    partners = partners[:20]
    
    serializer = PartnerSerializer(partners, many=True)
    
    return Response({
        'success': True,
        'partners': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def request_matching(request):
    """친구찾기 신청 API - 간단하고 명확한 로직"""
    user = request.user
    
    print(f"사용자 {user.id} ({user.nickname})의 매칭 신청 요청")
    print(f"요청 데이터: {request.data}")
    
    # 가장 최근 요청의 상태 확인
    latest_request = MatchingRequest.objects.filter(user=user).order_by('-created_at').first()
    if latest_request and latest_request.status == 'pending':
        print(f"사용자 {user.id}의 최신 요청이 pending 상태: {latest_request.id}")
        return Response({
            'success': False,
            'message': '이미 매칭 신청이 진행 중입니다. 관리자가 승인할 때까지 기다려주세요.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 새로운 매칭 요청 생성
    serializer = MatchingRequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.validated_data['user'] = user
        matching_request = serializer.save()
        
        print(f"사용자 {user.id}의 새로운 매칭 요청 생성 성공: {matching_request.id}")
        return Response({
            'success': True,
            'message': '친구찾기 신청이 완료되었습니다.',
            'requestId': matching_request.id
        }, status=status.HTTP_201_CREATED)
    
    print(f"사용자 {user.id}의 매칭 요청 데이터 유효성 검사 실패: {serializer.errors}")
    return Response({
        'success': False,
        'message': f'친구찾기 신청 중 오류가 발생했습니다: {serializer.errors}'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_matching_status(request):
    """매칭 상태 확인 API - 가장 최근 요청의 상태를 기준으로 판단"""
    user = request.user
    
    # 가장 최근의 매칭 요청 확인 (created_at 기준으로 정렬)
    latest_request = MatchingRequest.objects.filter(user=user).order_by('-created_at').first()
    
    if not latest_request:
        # 아무 요청도 없으면 새로운 요청 허용
        return Response({
            'success': True,
            'status': 'none',
            'message': '새로운 매칭 요청이 가능합니다.'
        }, status=status.HTTP_200_OK)
    
    if latest_request.status == 'matched':
        # 가장 최근 요청이 matched면 새로운 요청 허용
        return Response({
            'success': True,
            'status': 'none',
            'message': '매칭이 완료되었습니다. 새로운 매칭 요청이 가능합니다.'
        }, status=status.HTTP_200_OK)
    
    elif latest_request.status == 'pending':
        # 가장 최근 요청이 pending이면 새로운 요청 차단
        return Response({
            'success': True,
            'status': 'pending',
            'message': '매칭 신청이 진행 중입니다.'
        }, status=status.HTTP_200_OK)
    
    else:
        # rejected 등 다른 상태면 새로운 요청 허용
        return Response({
            'success': True,
            'status': 'none',
            'message': '새로운 매칭 요청이 가능합니다.'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def simulate_matching(request):
    """매칭 시뮬레이션 API (관리자용)"""
    serializer = MatchingSimulateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'message': '매칭 시뮬레이션 중 오류가 발생했습니다.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user_id = serializer.validated_data['user_id']
    user = User.objects.get(id=user_id)
    
    try:
        matching_request = MatchingRequest.objects.get(user=user, status='pending')
        
        # 매칭할 파트너 찾기 (간단한 랜덤 매칭)
        preferences = matching_request.preferences
        
        # 매칭 조건에 맞는 사용자들 필터링
        queryset = User.objects.exclude(id=user.id)
        
        # 성별 필터링
        if matching_request.gender_preference != 'any':
            queryset = queryset.filter(gender=matching_request.gender_preference)
        
        # 대학교 필터링
        if matching_request.university_preference:
            if matching_request.university_preference == 'same_university':
                queryset = queryset.filter(university=user.university)
            elif matching_request.university_preference == 'specific_university':
                if matching_request.specific_university:
                    queryset = queryset.filter(school=matching_request.specific_university)
            else:
                queryset = queryset.filter(university=matching_request.university_preference)
        
        # 언어 매칭 필터링
        if preferences.teaching_languages and preferences.learning_languages:
            teaching_languages = preferences.teaching_languages
            learning_languages = preferences.learning_languages
            
            teaching_matches = Q()
            for lang in teaching_languages:
                teaching_matches |= Q(languages__language=lang, languages__language_type='learning')
            
            learning_matches = Q()
            for lang in learning_languages:
                learning_matches |= Q(languages__language=lang, languages__language_type='teaching')
            
            queryset = queryset.filter(teaching_matches & learning_matches)
        
        # 매칭할 파트너 선택
        available_partners = list(queryset.distinct())
        if available_partners:
            partner = random.choice(available_partners)
            
            # 매칭 완료
            matching_request.status = 'matched'
            matching_request.matched_partner = partner
            matching_request.save()
            
            # 채팅방 생성
            from chat.models import ChatRoom
            chat_room = ChatRoom.objects.create(user1=user, user2=partner)
            
            partner_serializer = PartnerSerializer(partner)
            
            return Response({
                'success': True,
                'message': '매칭이 성공적으로 완료되었습니다.',
                'partner': partner_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': '매칭할 수 있는 파트너가 없습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except MatchingRequest.DoesNotExist:
        return Response({
            'success': False,
            'message': '매칭 요청이 없습니다.'
        }, status=status.HTTP_400_BAD_REQUEST)


# 관리자용 API
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_all_matching_requests(request):
    """모든 매칭 요청 조회 (관리자용)"""
    # 관리자 권한 확인 (간단히 is_staff로 확인)
    if not request.user.is_staff:
        return Response({
            'success': False,
            'message': '관리자 권한이 필요합니다.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # 모든 요청 조회 (matched 상태도 포함하여 다중 매칭 허용)
    # 최신순으로 정렬 (created_at 기준)
    requests = MatchingRequest.objects.all().order_by('-created_at', '-id')
    serializer = AdminMatchingRequestSerializer(requests, many=True)
    
    return Response({
        'success': True,
        'requests': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_partners(request):
    """사용 가능한 매칭 파트너 목록 조회"""
    if not request.user.is_staff:
        return Response({
            'success': False,
            'message': '관리자 권한이 필요합니다.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    request_id = request.GET.get('request_id')
    if not request_id:
        return Response({
            'success': False,
            'message': '요청 ID가 필요합니다.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        matching_request = MatchingRequest.objects.get(id=request_id)
    except MatchingRequest.DoesNotExist:
        return Response({
            'success': False,
            'message': '매칭 요청을 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # 요청자의 선호도 가져오기
    try:
        preference = matching_request.preferences
        learning_languages = preference.learning_languages
        teaching_languages = preference.teaching_languages
        gender_preference = matching_request.gender_preference
        university_preference = matching_request.university_preference
    except:
        return Response({
            'success': False,
            'message': '매칭 선호도 정보를 찾을 수 없습니다.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 매칭 가능한 사용자 찾기
    # 1. 요청자 본인만 제외 (이미 매칭된 사용자도 매칭 가능하도록 허용)
    potential_partners = User.objects.exclude(id=matching_request.user_id)
    
    # 2. 성별 선호도 필터링
    if gender_preference and gender_preference != 'any':
        potential_partners = potential_partners.filter(gender=gender_preference)
    
    # 3. 대학교 선호도 필터링
    if university_preference and university_preference != 'any':
        if university_preference == 'same':
            potential_partners = potential_partners.filter(
                university=matching_request.user.university
            )
        elif university_preference == 'different':
            potential_partners = potential_partners.exclude(
                university=matching_request.user.university
            )
    
    # 4. 관리자가 자유롭게 선택할 수 있도록 모든 사용자 표시 (언어 조건 제거)
    matching_partners = list(potential_partners)
    
    # 파트너 정보 직렬화
    partner_data = []
    for partner in matching_partners:
        partner_teaching = [lang.language for lang in partner.languages.filter(language_type='teaching')]
        partner_learning = [lang.language for lang in partner.languages.filter(language_type='learning')]
        partner_interests = [interest.interest for interest in partner.interests.all()]
        
        # 해당 파트너가 이미 매칭되었는지 확인
        is_matched = MatchingRequest.objects.filter(
            user=partner, 
            status='matched'
        ).exists()
        
        partner_data.append({
            'id': partner.id,
            'nickname': partner.nickname,
            'gender': partner.gender,
            'school': partner.school,
            'university': partner.university,
            'profile_image': partner.profile_image,
            'teaching_languages': partner_teaching,
            'learning_languages': partner_learning,
            'interests': partner_interests,
            'is_matched': is_matched
        })
    
    return Response({
        'success': True,
        'partners': partner_data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_matching_request(request, request_id):
    """매칭 요청 승인 (관리자용)"""
    
    if not request.user.is_staff:
        return Response({
            'success': False,
            'message': '관리자 권한이 필요합니다.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # 모든 상태의 매칭 요청 승인 가능 (사용자는 계속 매칭 가능)
        matching_request = MatchingRequest.objects.get(id=request_id)
        # 프론트엔드에서 선택한 파트너 ID 받기
        partner_id = request.data.get('partner_id')
        if not partner_id:
            return Response({
                'success': False,
                'message': '파트너 ID가 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            partner = User.objects.get(id=partner_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': '선택한 파트너를 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 기존 pending 요청을 matched로 변경
        matching_request.status = 'matched'
        matching_request.matched_partner = partner
        matching_request.save()
        
        # 파트너의 기존 pending 요청이 있으면 matched로 변경, 없으면 새로 생성
        partner_pending_request = MatchingRequest.objects.filter(user=partner, status='pending').first()
        if partner_pending_request:
            # 파트너의 기존 pending 요청을 matched로 변경
            partner_pending_request.status = 'matched'
            partner_pending_request.matched_partner = matching_request.user
            partner_pending_request.save()
        else:
            # 파트너의 pending 요청이 없으면 새로 생성
            MatchingRequest.objects.create(
                user=partner,
                status='matched',
                matched_partner=matching_request.user,
                gender_preference='무관',
                university_preference='무관',
                specific_university=''
            )
        
        # 채팅방 생성 (기존 매칭과 독립적으로)
        from chat.models import ChatRoom
        try:
            # 기존 채팅방이 있는지 확인
            existing_chat = ChatRoom.objects.filter(
                user1=matching_request.user, 
                user2=partner
            ).first()
            
            if not existing_chat:
                existing_chat = ChatRoom.objects.filter(
                    user1=partner, 
                    user2=matching_request.user
                ).first()
            
            if existing_chat:
                chat_room = existing_chat
            else:
                chat_room = ChatRoom.objects.create(
                    user1=matching_request.user, 
                    user2=partner
                )
        except Exception as e:
            # 채팅방 생성 실패해도 매칭은 성공으로 처리
            chat_room = None
        
        # 파트너가 이미 매칭된 상태인지 확인
        partner_existing_matches = MatchingRequest.objects.filter(
            user=partner, 
            status='matched'
        ).count()
        
        # 파트너의 기존 매칭 정보도 함께 반환
        partner_existing_partners = []
        if partner_existing_matches > 0:
            existing_requests = MatchingRequest.objects.filter(
                user=partner, 
                status='matched'
            ).select_related('matched_partner')
            partner_existing_partners = [
                {
                    'id': req.matched_partner.id,
                    'nickname': req.matched_partner.nickname
                } for req in existing_requests if req.matched_partner is not None
            ]
        
        return Response({
            'success': True,
            'message': '매칭이 성공적으로 승인되었습니다.',
            'partner_id': partner.id,
            'partner_name': partner.nickname,
            'chat_room_id': existing_chat.id if 'existing_chat' in locals() and existing_chat else None,
            'partner_existing_matches': partner_existing_matches,
            'partner_existing_partners': partner_existing_partners
        }, status=status.HTTP_200_OK)
            
    except MatchingRequest.DoesNotExist:
        return Response({
            'success': False,
            'message': '매칭 요청을 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_matching_request(request, request_id):
    """매칭 요청 거부 (관리자용)"""
    if not request.user.is_staff:
        return Response({
            'success': False,
            'message': '관리자 권한이 필요합니다.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        matching_request = MatchingRequest.objects.get(id=request_id, status='pending')
        matching_request.status = 'rejected'
        matching_request.save()
        
        return Response({
            'success': True,
            'message': '매칭 요청이 거부되었습니다.'
        }, status=status.HTTP_200_OK)
        
    except MatchingRequest.DoesNotExist:
        return Response({
            'success': False,
            'message': '매칭 요청을 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_matched_partner(request, request_id):
    """매칭된 파트너 정보 조회 (관리자용)"""
    if not request.user.is_staff:
        return Response({
            'success': False,
            'message': '관리자 권한이 필요합니다.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        matching_request = MatchingRequest.objects.get(id=request_id)
        
        if matching_request.status != 'matched' or not matching_request.matched_partner:
            return Response({
                'success': False,
                'message': '매칭된 파트너가 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        partner = matching_request.matched_partner
        
        # 파트너의 언어 정보 가져오기
        partner_teaching = [lang.language for lang in partner.languages.filter(language_type='teaching')]
        partner_learning = [lang.language for lang in partner.languages.filter(language_type='learning')]
        partner_interests = [interest.interest for interest in partner.interests.all()]
        
        partner_data = {
            'id': partner.id,
            'nickname': partner.nickname,
            'gender': partner.gender,
            'school': partner.school,
            'university': partner.university,
            'profile_image': partner.profile_image,
            'teaching_languages': partner_teaching,
            'learning_languages': partner_learning,
            'interests': partner_interests,
        }
        
        return Response({
            'success': True,
            'partner': partner_data
        }, status=status.HTTP_200_OK)
        
    except MatchingRequest.DoesNotExist:
        return Response({
            'success': False,
            'message': '매칭 요청을 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)