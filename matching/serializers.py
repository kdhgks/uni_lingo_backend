from rest_framework import serializers
from users.models import User
from .models import MatchingRequest, MatchingPreference


class PartnerSerializer(serializers.ModelSerializer):
    """파트너 정보 시리얼라이저"""
    teaching_languages = serializers.SerializerMethodField()
    learning_languages = serializers.SerializerMethodField()
    interests = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'nickname', 'profile_image', 'gender', 'university',
            'teaching_languages', 'learning_languages', 'interests', 'age'
        ]
    
    def get_teaching_languages(self, obj):
        """가르치는 언어들 반환"""
        return [lang.language for lang in obj.languages.filter(language_type='teaching')]
    
    def get_learning_languages(self, obj):
        """배우는 언어들 반환"""
        return [lang.language for lang in obj.languages.filter(language_type='learning')]
    
    def get_interests(self, obj):
        """관심사들 반환"""
        return [interest.interest for interest in obj.interests.all()]
    
    def get_age(self, obj):
        """나이 계산"""
        if obj.birth_date:
            from datetime import date
            today = date.today()
            return today.year - obj.birth_date.year - ((today.month, today.day) < (obj.birth_date.month, obj.birth_date.day))
        return None


class MatchingRequestSerializer(serializers.ModelSerializer):
    """매칭 요청 시리얼라이저"""
    teaching_languages = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False
    )
    learning_languages = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False
    )
    interests = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = MatchingRequest
        fields = [
            'gender_preference', 'university_preference', 'specific_university',
            'teaching_languages', 'learning_languages', 'interests'
        ]
    
    def create(self, validated_data):
        """매칭 요청 생성"""
        # 언어 및 관심사 데이터 분리
        teaching_languages = validated_data.pop('teaching_languages', [])
        learning_languages = validated_data.pop('learning_languages', [])
        interests = validated_data.pop('interests', [])
        
        # 매칭 요청 생성
        matching_request = MatchingRequest.objects.create(**validated_data)
        
        # 매칭 선호도 생성
        preference = MatchingPreference.objects.create(
            matching_request=matching_request,
            teaching_languages=teaching_languages,
            learning_languages=learning_languages,
            interests=interests
        )
        
        return matching_request


class MatchingStatusSerializer(serializers.ModelSerializer):
    """매칭 상태 시리얼라이저"""
    partner = PartnerSerializer(read_only=True)
    
    class Meta:
        model = MatchingRequest
        fields = ['id', 'status', 'partner', 'created_at']


class MatchingSimulateSerializer(serializers.Serializer):
    """매칭 시뮬레이션 시리얼라이저"""
    user_id = serializers.IntegerField()
    
    def validate_user_id(self, value):
        """사용자 ID 검증"""
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 사용자입니다.")
        return value


class AdminMatchingRequestSerializer(serializers.ModelSerializer):
    """관리자용 매칭 요청 시리얼라이저"""
    user = serializers.SerializerMethodField()
    learning_languages = serializers.SerializerMethodField()
    teaching_languages = serializers.SerializerMethodField()
    interests = serializers.SerializerMethodField()
    matched_partner = serializers.SerializerMethodField()
    matched_at = serializers.SerializerMethodField()
    
    class Meta:
        model = MatchingRequest
        fields = [
            'id', 'status', 'user', 'gender_preference', 'university_preference', 
            'specific_university', 'learning_languages', 'teaching_languages', 
            'interests', 'matched_partner', 'matched_at', 'created_at', 'updated_at'
        ]
    
    def get_user(self, obj):
        """사용자 정보 반환"""
        return {
            'id': obj.user.id,
            'nickname': obj.user.nickname,
            'gender': obj.user.gender,
            'school': obj.user.school,
            'university': obj.user.university,
            'profile_image': obj.user.profile_image
        }
    
    def get_learning_languages(self, obj):
        """배우고 싶은 언어들 반환"""
        try:
            return obj.preferences.learning_languages
        except:
            return []
    
    def get_teaching_languages(self, obj):
        """가르칠 수 있는 언어들 반환"""
        try:
            return obj.preferences.teaching_languages
        except:
            return []
    
    def get_interests(self, obj):
        """관심사들 반환"""
        try:
            return obj.preferences.interests
        except:
            return []
    
    def get_matched_partner(self, obj):
        """매칭된 파트너 정보 반환"""
        if obj.status == 'matched' and obj.matched_partner:
            partner = obj.matched_partner
            return {
                'id': partner.id,
                'nickname': partner.nickname,
                'gender': partner.gender,
                'school': partner.school,
                'university': partner.university,
                'profile_image': partner.profile_image,
                'teaching_languages': [lang.language for lang in partner.languages.filter(language_type='teaching')],
                'learning_languages': [lang.language for lang in partner.languages.filter(language_type='learning')],
                'interests': [interest.interest for interest in partner.interests.all()]
            }
        return None
    
    def get_matched_at(self, obj):
        """매칭 완료 시간 반환"""
        if obj.status == 'matched':
            return obj.updated_at
        return None
