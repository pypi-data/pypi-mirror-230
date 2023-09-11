from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        exclude = ('password',)
    
class UserCreationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('username','email','first_name','last_name','password')
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user
    
class UserUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('username','email','first_name','last_name')
    
class UserChangePasswordSerializer(serializers.Serializer):
    
    password = serializers.CharField(max_length=100,write_only=True)
    new_password = serializers.CharField(max_length=100,write_only=True)
        
    def is_valid(self, *, raise_exception=False):
        
        valid = super().is_valid(raise_exception=raise_exception)
        
        password = self.validated_data.get("password")
        if not self.instance.check_password(password):
            self._errors['password'] = ['Password is incorrect']
            valid = False
        
        return valid

    def update(self, instance:User, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance