from django.urls import path
from .views import UserRegisterView, BorrowBookView, ReturnBookView, BookListView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', UserRegisterView.as_view()),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('books/<int:book_id>/borrow/', BorrowBookView.as_view(), name='borrow-book'),
    path('borrows/<int:borrow_id>/return/', ReturnBookView.as_view(), name='return-book'),
    path('books/', BookListView.as_view(), name='book-list')
]