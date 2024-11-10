from django.urls import path
from .views import HomepageView, BookDetailView, UserProfileView, DepositMoneyView, BorrowingView

app_name = 'library'

urlpatterns = [
    path('', HomepageView.as_view(), name='homepage'),
    path('user_profile/', UserProfileView.as_view(), name='user_profile'),
    path('deposit_money/', DepositMoneyView.as_view(), name='deposit_money'),
    path('book_detail/<int:id>/', BookDetailView.as_view(), name='book_detail'),
    path('borrowing_book/<int:id>/', BorrowingView.as_view(), name='borrowing'),
]
