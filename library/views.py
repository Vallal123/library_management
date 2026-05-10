from rest_framework.views import APIView
from .models import User, Book, Author, BorrowRecord
from django.utils import timezone
from datetime import datetime
from .serializers import UserRegisterSerializer, BookListSerializer, UserLoginSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView
from django.db import transaction
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
import os
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            try:
                send_mail(
                    subject="Welcome to the Smart Library",
                    message=f"Hi {user.username}, thanks for joining! Explore our AI-powered recommendations.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Email failed: {e}")

            return Response(serializer.data, status=201)
        
        return Response(serializer.errors, status=400)
    
class UserLoginView(APIView):
    
    permission_classes = [AllowAny]

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
    serializer_class = BookListSerializer

    def get_queryset(self):
        return Book.objects.filter(is_active=True).prefetch_related('authors', 'genres')


class BorrowBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):
        try:
            with transaction.atomic():

                book = Book.objects.select_for_update().get(id=book_id)

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
        
