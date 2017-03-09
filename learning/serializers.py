from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Categories, User

class CategoriesSerializer(serializers.ModelSerializer):
	class Meta:
		model = Categories
		fields = ('category', 'description')


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('email','password','firstName', 'lastName')
		extra_kwargs = {
			'password': {'write_only': True}
		}
	
	def create(self, validated_data):
		user = User(
				email = validated_data['email'],
				firstName = validated_data['firstName'],
				lastName = validated_data['lastName']
			)
		user.set_password(validated_data['password'])
		user.save()
		return user

	def get_user(self, email, password):
		user = User.objects.filter(email=email, password=password)
		if user:
			return user
		else:
			return None
