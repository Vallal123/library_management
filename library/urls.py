from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import (BookListView, BorrowBookView, BorrowedBookView,
                    ReturnBookView, UserRegisterView)

urlpatterns = [
    path('register/', UserRegisterView.as_view()),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/borrow/<int:book_id>/', BorrowBookView.as_view(), name='borrow-book'),
    path('books/return/<int:borrow_id>/', ReturnBookView.as_view(), name='return-book'),
    path('borrowed_books/', BorrowedBookView.as_view(), name='borrowed_books')
]