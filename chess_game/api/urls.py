from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
                    StartGameView,
                    OfferDrawView,
                    AcceptDrawView,
                    RejectDrawView,
                    ResignGameView,
                    MakeMoveView,
                    GameCurrentStateView,
                    GamePgnView,
                    SecureView
               )
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="ChessServer API",
        default_version='v1',
        description="API documentation for ChessServer project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="your-email@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('secure-endpoint/', SecureView.as_view(), name='secure_endpoint'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('start/', StartGameView.as_view(),
         name='start-game'),
    path('move/<int:pk>/', MakeMoveView.as_view(),
         name='make-move'),
    path('offer-draw/<int:pk>/', OfferDrawView.as_view(),
         name='offer-draw'),
    path('accept-draw/<int:pk>/', AcceptDrawView.as_view(),
         name='accept-draw'),
    path('reject-draw/<int:pk>/', RejectDrawView.as_view(),
         name='reject-draw'),
    path('resign-game/<int:pk>/', ResignGameView.as_view(),
         name='resign-game'),
    path('get-game/<int:pk>/', GameCurrentStateView.as_view(),
         name='get-game'),
    path('get-pgn/<int:pk>/', GamePgnView.as_view(),
         name='get-pgn'),
]