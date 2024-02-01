from django.urls import path
from . import views

urlpatterns = [
    path('tickets/', views.TicketListView.as_view(), name='ticket-list-api'),
    path('tickets/<int:pk>/', views.TicketDetailAPIView.as_view(), name='ticket-detail-api'),
    path('tickets/create/', views.TicketCreateAPIView.as_view(), name='ticket-create-api'),
    path('tickets/update/<int:pk>/', views.TicketUpdateAPIView.as_view(), name='ticket-update-api'),
    path('tickets/delete/<int:pk>/', views.TicketDeleteAPIView.as_view(), name='ticket-delete-api'),
    
    # Other API endpoints
    path('tickets/list/', views.ticket_list_api, name='ticket-list'),
    path('tickets/urgent/', views.urgent_ticket_list_api, name='urgent-ticket-list'),
    path('tickets/unresolved/', views.unresolved_tickets_api, name='unresolved-tickets'),
    path('tickets/mark_resolved/<int:id>/', views.mark_ticket_as_resolved_api, name='mark-ticket-resolved'),
    path('tickets/mark_unresolved/<int:id>/', views.mark_ticket_as_unresolved_api, name='mark-ticket-unresolved'),
    path('tickets/comment/<int:ticket_id>/', views.add_comment_api, name='add-comment'),
    path('tickets/search/', views.search_results_api, name='search-results'),
    path('tickets/staff_search/', views.staff_search_results_api, name='staff-search-results'),
    path('tickets/all_search/', views.all_search_results_api, name='all-search-results'),
    path('tickets/performance/', views.user_performance_api, name='user-performance'),
    path('tickets/performance/<str:username>/', views.user_performance_details_api, name='user-performance-details'),

    # Email retrieval endpoint
    path('retrieve_emails/', views.retrieve_emails, name='retrieve-emails-api'),
]
