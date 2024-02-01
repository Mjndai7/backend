from django.urls import include, path
from .views import BookSlotView, CreateSlotsForIntervalView, GetAvailableSlotsView, SlotDataView, SlotDetailsView

urlpatterns = [
    
    path('book/slot/<int:uid>/', BookSlotView.as_view(), name='book_slot'),
    path('book/<int:user_id>/slots/', GetAvailableSlotsView.as_view(), name='available_slots'),
    path('slot/<int:uid>/', SlotDetailsView.as_view(), name='slot_details'),
    path('slot/', SlotDataView.as_view(), name='slot_data'),
    path('slots/interval/', CreateSlotsForIntervalView.as_view(), name='slot_interval')
]