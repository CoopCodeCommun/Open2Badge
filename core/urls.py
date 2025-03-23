from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HomeViewSet, AuthViewSet, IssuerViewSet, PublicIssuerListView, BadgeClassViewSet, EndorsementViewSet
from .api import OpenBadgeViewSet

app_name = 'core'

# API routes
router = DefaultRouter()
router.register(r'badges', OpenBadgeViewSet, basename='badges')

# Home views
home_list = HomeViewSet.as_view({'get': 'list'})

# Auth views
auth_login = AuthViewSet.as_view({'get': 'login', 'post': 'login'})
auth_logout = AuthViewSet.as_view({'post': 'logout'})

# Issuer views
issuer_list = IssuerViewSet.as_view({'get': 'list'})
issuer_create = IssuerViewSet.as_view({'get': 'create', 'post': 'create'})
issuer_create_modal = IssuerViewSet.as_view({'get': 'create_modal'})
issuer_update_modal = IssuerViewSet.as_view({'get': 'update_modal'})
issuer_update = IssuerViewSet.as_view({'get': 'update', 'post': 'update'})
issuer_delete = IssuerViewSet.as_view({'get': 'delete', 'post': 'delete'})

# Badge views
badge_list = BadgeClassViewSet.as_view({'get': 'list'})
badge_detail = BadgeClassViewSet.as_view({'get': 'retrieve'})
badge_create = BadgeClassViewSet.as_view({'post': 'create'})
badge_create_modal = BadgeClassViewSet.as_view({'get': 'create_modal'})
badge_edit_modal = BadgeClassViewSet.as_view({'get': 'edit_modal'})
badge_update = BadgeClassViewSet.as_view({'post': 'update'})
badge_add_alignment_modal = BadgeClassViewSet.as_view({'get': 'add_alignment_modal'})
badge_add_alignment = BadgeClassViewSet.as_view({'post': 'add_alignment'})
badge_delete_alignment = BadgeClassViewSet.as_view({'delete': 'delete_alignment'})

urlpatterns = [
    # API routes
    path('api/v3/', include(router.urls)),
    # API URLs
    path('api/v3/', include(router.urls)),
    path('api/v3/badge-with-endorsements/', OpenBadgeViewSet.as_view({'get': 'badge_with_endorsements'}), name='badge-with-endorsements'),
    
    # Home URLs
    path('', home_list, name='home'),
    
    # Auth URLs
    path('login/', auth_login, name='login'),
    path('logout/', auth_logout, name='logout'),
    path('profile/', AuthViewSet.as_view({'get': 'profile', 'post': 'profile'}), name='profile'),
    path('profile/endorsement-badges/', AuthViewSet.as_view({'get': 'profile_endorsement_badges'}), name='profile-endorsement-badges'),
    path('verify-email/<str:token>/', AuthViewSet.as_view({'get': 'verify_email'}), name='verify-email'),
    path('resend-verification/', AuthViewSet.as_view({'post': 'resend_verification'}), name='resend-verification'),
    path('join-issuer/<int:issuer_id>/', AuthViewSet.as_view({'post': 'join_issuer'}), name='join-issuer'),
    path('leave-issuer/<int:issuer_id>/', AuthViewSet.as_view({'post': 'leave_issuer'}), name='leave-issuer'),
    
    # Issuer URLs
    path('issuers/', PublicIssuerListView.as_view(), name='issuer-list'),
    path('issuers/create/', issuer_create, name='issuer-create'),
    path('issuers/modal/create/', issuer_create_modal, name='issuer-create-modal'),
    path('issuers/<int:pk>/modal/update/', issuer_update_modal, name='issuer-update-modal'),
    path('issuers/<int:pk>/update/', issuer_update, name='issuer-update'),
    path('issuers/<int:pk>/delete/', issuer_delete, name='issuer-delete'),
    
    # Badge URLs
    path('badges/', badge_list, name='badge-list'),
    path('badges/<int:pk>/', badge_detail, name='badge-detail'),
    path('badges/create/', badge_create, name='badge-create'),
    path('badges/modal/create/', badge_create_modal, name='badge-create-modal'),
    path('badges/<int:pk>/modal/edit/', badge_edit_modal, name='badge-edit-modal'),
    path('badges/<int:pk>/update/', badge_update, name='badge-update'),
    path('badges/<int:pk>/alignment/modal/add/', badge_add_alignment_modal, name='badge-add-alignment-modal'),
    path('badges/<int:pk>/alignment/add/', badge_add_alignment, name='badge-add-alignment'),
    path('badges/<int:pk>/alignment/<int:alignment_pk>/delete/', badge_delete_alignment, name='badge-delete-alignment'),
    
    # Public Badge URLs
    path('badges/public/', BadgeClassViewSet.as_view({'get': 'public_list'}), name='public-badge-list'),
    path('badges/my-issuers/', BadgeClassViewSet.as_view({'get': 'my_issuers_badges'}), name='my-issuers-badges'),
    path('badges/endorsement/', BadgeClassViewSet.as_view({'get': 'endorsement_list'}), name='badge-endorsement-list'),
    
    # Endorsement URLs
    path('endorsement/modal/', EndorsementViewSet.as_view({'get': 'endorsement_modal'}), name='endorsement_modal'),
    path('endorsement/create/', EndorsementViewSet.as_view({'post': 'create_endorsement'}), name='create_endorsement'),
    path('endorsement/list/', EndorsementViewSet.as_view({'get': 'get_endorsements'}), name='get_endorsements'),
    path('endorsement/<str:endorsement_id>/edit/', EndorsementViewSet.as_view({'get': 'edit_endorsement_modal'}), name='edit_endorsement_modal'),
    path('endorsement/<str:endorsement_id>/update/', EndorsementViewSet.as_view({'post': 'update_endorsement'}), name='update_endorsement'),
    path('endorsement/<str:endorsement_id>/delete/', EndorsementViewSet.as_view({'delete': 'delete_endorsement'}), name='delete_endorsement'),
]
