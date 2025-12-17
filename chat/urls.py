from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('start/', views.start_chat, name='start'),
    path('start/<int:product_id>/', views.start_chat, name='start_with_product'),
    path('send/<int:session_id>/', views.send_message, name='send'),
    path('messages/<int:session_id>/', views.get_messages, name='messages'),
    path('close/<int:session_id>/', views.close_chat, name='close'),
]
