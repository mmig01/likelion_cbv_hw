from rest_framework import serializers
from .models import *


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    tag = serializers.SerializerMethodField()
    image = serializers.ImageField(use_url=True, required=False)
    comments = serializers.SerializerMethodField(read_only=True)
    username = serializers.SerializerMethodField(read_only = True)

    def get_username(self, instance):
        return instance.user.username
    
    def get_comments(self, instance):
        serializer = CommentSerializer(instance.comments, many=True)
        return serializer.data
    
    def get_tag(self, instance):
        tags = instance.tag.all()
        return [tag.name for tag in tags]
    
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'comments',
            'like_count',
            'like'
        ]


class PostListSerializer(serializers.ModelSerializer): 
    comments_cnt = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField(read_only = True)

    def get_username(self, instance):
        return instance.user.username
    
    def get_comments_cnt(self, instance):
        return instance.comments.count()
    
    def get_tag(self, instance):
        tags = instance.tag.all()
        return [tag.name for tag in tags]

    class Meta:
        model = Post
        fields = ['id', 'name', 'username', 'content', 'created_at', 'updated_at', 'comments_cnt', 'tag', 'image', 'like_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'comments_cnt', 'like_count']
        
class CommentSerializer(serializers.ModelSerializer):
    post = serializers.SerializerMethodField()

    # 게시물 제목을 확인할 수 있게 함
    def get_post(self, instance):
        return instance.post.name
    
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['post']