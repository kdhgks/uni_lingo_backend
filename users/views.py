from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import User, UserLanguage, UserInterest
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    ChangePasswordSerializer, DeleteAccountSerializer
)

User = get_user_model()


def get_tokens_for_user(user):
    """사용자에 대한 JWT 토큰 생성"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """로그인 API"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        user_serializer = UserSerializer(user)
        
        return Response({
            'success': True,
            'token': tokens['access'],
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': '이메일 또는 비밀번호가 올바르지 않습니다.'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    """회원가입 API"""
    import json
    
    # FormData 처리
    data = request.POST.copy()
    files = request.FILES
    
    # 전화번호 형식 변환 (010-1234-5678 -> 01012345678)
    if 'phone' in data:
        phone = data['phone'].replace('-', '')
        data['phone'] = phone
    
    # 파일 데이터 추가
    if 'student_card' in files:
        data['student_card'] = files['student_card']
    
    # JSON 문자열로 전송된 언어 데이터 파싱
    if 'learning_languages' in data and isinstance(data['learning_languages'], str):
        try:
            data['learning_languages'] = json.loads(data['learning_languages'])
        except json.JSONDecodeError:
            data['learning_languages'] = []
    
    if 'teaching_languages' in data and isinstance(data['teaching_languages'], str):
        try:
            data['teaching_languages'] = json.loads(data['teaching_languages'])
        except json.JSONDecodeError:
            data['teaching_languages'] = []
    
    if 'interests' in data and isinstance(data['interests'], str):
        try:
            data['interests'] = json.loads(data['interests'])
        except json.JSONDecodeError:
            data['interests'] = []
    
    serializer = UserRegistrationSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        
        # 언어 정보 저장
        learning_languages = data.get('learning_languages', [])
        for language in learning_languages:
            UserLanguage.objects.create(
                user=user,
                language=language,
                language_type='learning'
            )
        
        teaching_languages = data.get('teaching_languages', [])
        for language in teaching_languages:
            UserLanguage.objects.create(
                user=user,
                language=language,
                language_type='teaching'
            )
        
        # 관심사 저장
        interests = data.get('interests', [])
        # JSON 문자열인 경우 파싱
        if isinstance(interests, str):
            import json
            try:
                interests = json.loads(interests)
            except json.JSONDecodeError:
                # JSON 파싱 실패시 쉼표로 분리
                interests = [interest.strip() for interest in interests.split(',') if interest.strip()]
        for interest in interests:
            UserInterest.objects.create(user=user, interest=interest)
        
        tokens = get_tokens_for_user(user)
        user_serializer = UserSerializer(user)
        
        return Response({
            'success': True,
            'token': tokens['access'],
            'user': user_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """프로필 조회/수정 API"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """프로필 수정"""
        try:
            user = self.get_object()
            data = request.data.copy()
            
            print(f"프로필 업데이트 요청 받음: {data}")
            print(f"사용자: {user.email}")
            
            # 언어 정보 처리
            if 'teaching_languages' in data:
                teaching_languages = data.pop('teaching_languages')
                # JSON 문자열인 경우 파싱
                if isinstance(teaching_languages, str):
                    import json
                    teaching_languages = json.loads(teaching_languages)
                # 기존 teaching 언어 삭제
                user.languages.filter(language_type='teaching').delete()
                # 새로운 teaching 언어 추가
                for language in teaching_languages:
                    UserLanguage.objects.create(
                        user=user,
                        language=language,
                        language_type='teaching'
                    )
            
            if 'learning_languages' in data:
                learning_languages = data.pop('learning_languages')
                # JSON 문자열인 경우 파싱
                if isinstance(learning_languages, str):
                    import json
                    learning_languages = json.loads(learning_languages)
                # 기존 learning 언어 삭제
                user.languages.filter(language_type='learning').delete()
                # 새로운 learning 언어 추가
                for language in learning_languages:
                    UserLanguage.objects.create(
                        user=user,
                        language=language,
                        language_type='learning'
                    )
            
            # 관심사 처리
            if 'interests' in data:
                interests = data.pop('interests')
                # JSON 문자열인 경우 파싱
                if isinstance(interests, str):
                    import json
                    try:
                        interests = json.loads(interests)
                    except json.JSONDecodeError:
                        # JSON 파싱 실패시 쉼표로 분리
                        interests = [interest.strip() for interest in interests.split(',') if interest.strip()]
                
                # 기존 관심사 삭제
                user.interests.all().delete()
                
                # 새로운 관심사 추가
                for interest in interests:
                    try:
                        UserInterest.objects.create(user=user, interest=interest)
                    except Exception as e:
                        pass
            
            # 나머지 필드 업데이트
            serializer = self.get_serializer(user, data=data, partial=True)
            if serializer.is_valid():
                try:
                    serializer.save()
                    
                    # 업데이트된 사용자 정보 반환
                    updated_user_serializer = UserSerializer(user, context={'request': self.request})
                    user_data = updated_user_serializer.data
                    
                    return Response({
                        'success': True,
                        'message': '프로필이 성공적으로 업데이트되었습니다.',
                        'user': user_data
                    }, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({
                        'success': False,
                        'message': f'프로필 업데이트 중 오류가 발생했습니다: {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'success': False,
                'message': '프로필 업데이트 중 오류가 발생했습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(f"프로필 업데이트 중 에러 발생: {e}")
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'message': f'프로필 업데이트 중 오류가 발생했습니다: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_account(request):
    """계정 삭제 API"""
    serializer = DeleteAccountSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        user.delete()
        
        return Response({
            'success': True,
            'message': '계정이 성공적으로 삭제되었습니다.'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': '계정 삭제 중 오류가 발생했습니다.'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_profile(request, user_id):
    """특정 사용자 프로필 조회 API (관리자용)"""
    try:
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': '사용자를 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """비밀번호 변경 API"""
    serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
    
    if serializer.is_valid():
        # 현재 비밀번호 확인
        current_password = serializer.validated_data['current_password']
        if not request.user.check_password(current_password):
            return Response({
                'success': False,
                'message': '현재 비밀번호가 올바르지 않습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 새 비밀번호 설정
        new_password = serializer.validated_data['new_password']
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({
            'success': True,
            'message': '비밀번호가 성공적으로 변경되었습니다.'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)