from rest_framework import serializers
from .models import Book, Author, Genre, User


class UserRegisterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'username', 
            'email', 'phone', 'address', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['name']

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']

class BookListSerializer(serializers.ModelSerializer):
    authors = serializers.StringRelatedField(many=True)
    genres = serializers.StringRelatedField(many=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'isbn', 'authors', 'genres',
            'available_copies', 'cover_image'
        ]
"""
class BookCreateSerializers(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(many=True, queryset=Author.objects.all())
    category = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())

    class Meta:
        model = Book
        fields = ['title', 'isbn', 'description', 'author', 'category', 'edition', 'page_count', 'total_copies', 'cover_image']

class BookUpdateSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(many=True, queryset=Author.objects.all())
    category = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())
    
    class Meta:
        model = Book
        fields = ['title', 'description', 'author', 'category', 'edition', 'page_count', 'cover_image', 'is_active']
        read_only_fields = ['isbn', 'total_copies', 'available_copies']

"""