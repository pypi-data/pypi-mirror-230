from drf_spectacular.utils import extend_schema
from garpix_user.models import UserSession
from garpix_user.utils.drf_spectacular import user_session_token_header_parameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from .models import Favorite
from .serializers import FavoriteSerializer
from rest_framework.generics import get_object_or_404


@extend_schema(
    parameters=[
        user_session_token_header_parameter()
    ]
)
class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = FavoriteSerializer

    def get_serializer_class(self):
        return FavoriteSerializer

    def get_queryset(self):
        user = UserSession.get_from_request(self.request)
        return Favorite.objects.filter(
            user_session=user
        )

    def perform_create(self, serializer):
        user = UserSession.get_from_request(self.request)
        serializer.save(
            user_session=user
        )

    @action(methods=['GET'], detail=False, url_path='current')
    def get_user_favorites(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['DELETE'], detail=False, url_path='(?P<model_name>[^/.]+)/(?P<object_id>[^/.]+)')
    def delete(self, request, model_name, object_id, *args, **kwargs):
        user = UserSession.get_or_create_user_session(request)
        content_type = ContentType.objects.get(model=model_name.lower())

        instance = obj = get_object_or_404(self.get_queryset(), content_type=content_type, object_id=object_id,
                                           user_session=user)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
