from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Author, Book, BorrowRecord, User
from .pagination import BookPagination
from .permissions import IsUser
from .serializers import (BookListSerializer, BorrowedBookSerializer,
                          UserRegisterSerializer)
from .tasks import send_welcome_email_task


class UserRegisterView(APIView):

    throttle_scope = 'auth'

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            send_welcome_email_task.delay(user.id)
            
            return Response({
                            "message": "User created successfully",
                            "username": user.username,
                            }, status=201)
        
        return Response(serializer.errors, status=400)
    
class UserLoginView(APIView):
    
    permission_classes = [AllowAny]
    throttle_scope = 'auth'

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'username': user.username,
                'email': user.email
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
class BookListView(ListAPIView):

    permission_classes = [AllowAny]
    throttle_scope = 'user'
    serializer_class = BookListSerializer
    pagination_class = BookPagination


    def get_queryset(self):
        return Book.objects.filter(is_active=True).prefetch_related('authors', 'genres')


class BorrowBookView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
            summary="Borrow a book",
            description="Allows and authenticated user to borrow a copy of a book if available.",
            responses={201: {"message": "Successfully borrowed..."}}
    )
    def post(self, request, book_id):
        try:
            with transaction.atomic():

                book = Book.objects.select_for_update().get(id=book_id)
                
                has_active_borrow = BorrowRecord.objects.filter(user=request.user, book=book, is_returned=False)
      

                if has_active_borrow:
                    return Response({
                        'error': f'You currently have an unreturned copy of {book.title}'
                    }, status=400)

                if book.available_copies <= 0:
                    return Response(
                        {"error": "No copies available at the moment."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                BorrowRecord.objects.create(
                    user=request.user,
                    book=book
                )

                book.reduce_copies(1)

                return Response(
                    {"message": f"Successfully borrowed '{book.title}'!"},
                    status=status.HTTP_201_CREATED
                )
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=404)

        except Exception as e:
            return Response({"error": str(e)}, status=400)   

class ReturnBookView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, borrow_id):
        try:
            with transaction.atomic():

                record = BorrowRecord.objects.select_for_update().get(
                    id=borrow_id,
                    user=request.user,
                    is_returned=False
                )

                record.return_date = timezone.now()
                record.save()

                book = record.book
                book.available_copies += 1
                book.save()

                is_late = record.is_overdue()

                return Response({
                    "message": f"Successfully returned '{book.title}'.",
                    "overdue": is_late,
                    "return_date": record.return_date
                }, status=status.HTTP_200_OK)
        
        except BorrowRecord.DoesNotExist:
            return Response(
                {"error": "Active borrow record not found or already returned."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class BorrowedBookView(ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = BorrowedBookSerializer

    def get_queryset(self):
        queryset = BorrowRecord.objects.filter(user=self.request.user).select_related('book', 'user')
        return queryset