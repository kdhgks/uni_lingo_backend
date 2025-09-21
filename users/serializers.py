from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserLanguage, UserInterest


class UserLanguageSerializer(serializers.ModelSerializer):
    """사용자 언어 시리얼라이저"""
    class Meta:
        model = UserLanguage
        fields = ['language', 'language_type']


class UserInterestSerializer(serializers.ModelSerializer):
    """사용자 관심사 시리얼라이저"""
    class Meta:
        model = UserInterest
        fields = ['interest']


class UserSerializer(serializers.ModelSerializer):
    """사용자 시리얼라이저"""
    teaching_languages = serializers.SerializerMethodField()
    learning_languages = serializers.SerializerMethodField()
    interests = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'nickname', 'profile_image', 'phone', 'gender', 
            'birth_date', 'student_name', 'school', 'department', 'student_id', 
            'university', 'teaching_languages', 'learning_languages', 'interests',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_teaching_languages(self, obj):
        """가르치는 언어들 반환"""
        return [lang.language for lang in obj.languages.filter(language_type='teaching')]
    
    def get_learning_languages(self, obj):
        """배우는 언어들 반환"""
        return [lang.language for lang in obj.languages.filter(language_type='learning')]
    
    def get_interests(self, obj):
        """관심사들 반환"""
        return [interest.interest for interest in obj.interests.all()]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """사용자 회원가입 시리얼라이저"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'nickname', 'phone', 'gender', 
            'birth_date', 'student_name', 'school', 'department', 'student_id', 
            'university', 'student_card'
        ]
    
    def validate(self, attrs):
        """비밀번호 확인 검증"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return attrs
    
    def create(self, validated_data):
        """사용자 생성"""
        # 비밀번호 확인 필드 제거
        validated_data.pop('password_confirm')
        
        # username을 email과 동일하게 설정 (Django 요구사항)
        validated_data['username'] = validated_data['email']
        
        # 사용자 생성
        user = User.objects.create_user(**validated_data)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """사용자 로그인 시리얼라이저"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        """로그인 검증"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('이메일 또는 비밀번호가 올바르지 않습니다.')
            if not user.is_active:
                raise serializers.ValidationError('비활성화된 계정입니다.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('이메일과 비밀번호를 모두 입력해주세요.')
        
        return attrs


class DeleteAccountSerializer(serializers.Serializer):
    """계정 삭제 시리얼라이저"""
    password = serializers.CharField()
    
    def validate_password(self, value):
        """비밀번호 검증"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("비밀번호가 올바르지 않습니다.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """비밀번호 변경 시리얼라이저"""
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    
    def validate_new_password(self, value):
        """새 비밀번호 검증"""
        validate_password(value)
        return value
    
    def validate(self, attrs):
        """전체 데이터 검증"""
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        
        # 현재 비밀번호와 새 비밀번호가 같은지 확인
        if current_password == new_password:
            raise serializers.ValidationError("새 비밀번호는 현재 비밀번호와 달라야 합니다.")
        
        return attrs
