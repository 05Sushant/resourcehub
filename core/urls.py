from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('resources/', views.ResourceListView.as_view(), name='resource-list'),
    path('reservations/', views.ReservationCreateView.as_view(), name='reservation-create'),
    path('reservations/<int:reservation_id>/cancel/',views.ReservationCancelView.as_view(),name='reservation-cancel'),
]
