from rest_framework.response import Response
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from .models import Post, Comment, Tag
from .serializers import PostSerializer, PostListSerializer, CommentSerializer, TagSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsPostOwnerOrReadOnly, IsCommentOwnerOrReadOnly
from rest_framework.exceptions import PermissionDenied

from django.shortcuts import get_object_or_404

# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.action == 'list' :
            return PostListSerializer
        else :
            return PostSerializer

    def get_permissions(self):
        if self.action in ["update", "create", "destroy", "partial_update"]:
            return [IsPostOwnerOrReadOnly()]
        return []

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        movie = serializer.instance
        self.handle_tags(movie)

        return Response(serializer.data)

    def perform_update(self, serializer):
        movie = serializer.save()
        movie.tag.clear()
        self.handle_tags(movie)

    def handle_tags(self, movie):
        tags = [word[1:] for word in movie.content.split(' ') if word.startswith('#')]
        for t in tags:
            tag, created = Tag.objects.get_or_create(name=t)
            movie.tag.add(tag)
        movie.save()
    
    @action(methods=['GET'], detail=False, url_path="mingi")
    def recommand(self, request):
        ran_post = self.get_queryset().order_by('?').first()
        ran_post_serializer = PostSerializer(ran_post)
        return Response(ran_post_serializer.data)
    

    @action(methods=['GET'], detail=True, url_path="likes")
    def likes(self, request, pk=None):
        post = self.get_queryset().filter(id=pk).first()
        if request.user in post.like.all():
            post.like.remove(request.user)
            post.like_count -= 1
            post.save()
        else:
            post.like.add(request.user)
            post.like_count += 1
            post.save()
        post_serializer = PostSerializer(post)
        return Response(post_serializer.data)
    
    @action(methods=['GET'], detail=False, url_path="likes_three")
    def like_three(self, request, pk=None):
        posts = self.get_queryset().order_by('-like_count')[:3]
        post_serializer = PostSerializer(posts, many=True)
        return Response(post_serializer.data)
    
# 댓글 디테일 조회 수정 삭제
class CommentViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    # 반환된 리스트의 각 권한 클래스가 순서대로 검사되어
    # 모든 권한 검사를 통과한 경우에만 뷰셋의 해당 액션이 실행
    def get_permissions(self):
        if self.action in ["update", "destroy", "partial_update"]:
            return [IsCommentOwnerOrReadOnly()]
        return []

    # 부모 클래스의 get_object 메서드를 호출하여 요청된 객체를 가져오고 이를 반환
    # 주로 객체를 조회하는 요청(예: retrieve, update, destroy 등)에서 호출
    def get_object(self):
        obj = super().get_object()
        return obj
    
# 게시물에 있는 댓글 목록 조회, 게시물에 댓글 작성
class PostCommentViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsCommentOwnerOrReadOnly()]
        return []
    
    def get_queryset(self):
        post = self.kwargs.get("post_id")
        queryset = Comment.objects.filter(post_id=post)
        return queryset
    
    def create(self, request, post_id=None):
        post = get_object_or_404(Post, id = post_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post)
        return Response(serializer.data)
    
# 디테일만 가져오기
class TagViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "name"
    lookup_url_kwarg = "tag_name"

    def retrieve(self, request, *args, **kwargs):
        tag_name = kwargs.get("tag_name")
        tag = get_object_or_404(Tag, name=tag_name)
        posts = Post.objects.filter(tag=tag)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


