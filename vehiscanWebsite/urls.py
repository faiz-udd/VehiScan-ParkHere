from django.urls import path
from . import views, WebPaths

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register, name='register-user'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('account', views.account, name='account'),
    
    path(WebPaths.PARKING_LOTS, views.parking_lots, name='parking-lots'),
    path(f'{WebPaths.PARKING_LOT}/<int:parking_lot_id>', views.parking_lot, name='parking-lot-detail'),
    path(WebPaths.REGISTER_USER, views.register_user, name='register-user'),
    path(WebPaths.PARKING_LOT_MONITORS, views.parking_lot_monitors, name='parking-lot-monitors'),
    path(f'{WebPaths.PARKING_LOT_MONITOR}/<int:parking_lot_monitor_id>', views.parking_lot_monitor, name='parking-lot-monitor'),
    
   
    path(WebPaths.PRIVACY_POLICY, views.privacy_policy, name='privacy-policy'),
    path('account/settings/', views.account_settings, name='account_settings'),
    path('account/security/', views.security_settings, name='security_settings'),
    
    path('account/create_listing/', views.create_listing, name='create_listing'),
    
    path('account/edit_listing/<int:listing_id>/', views.edit_listing, name='edit_listing'),
    path('listing/<int:pk>/edit/', views.edit_listing, name='edit_listing'),
    path('listing/<int:pk>/delete/', views.delete_listing, name='delete_listing'),
    path('listing/<int:pk>/view/', views.view_listing, name='view_listing'),
]