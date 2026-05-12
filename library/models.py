from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import datetime
from django.db.models import Q, F

def get_upload_path(instance, filename):
    ext = filename.split('.')
    return f"books/{instance.isbn}_{instance.title}.{ext[-1]}"

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.first_name

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'genre'
        verbose_name = 'genre'
        verbose_name_plural = 'genres'

    def __str__(self):
        return self.name
    
class Author(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'authors'
        verbose_name = 'author'
        verbose_name_plural = 'authors'

    def __str__(self):
        return self.name
    
class Book(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    isbn = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    authors = models.ManyToManyField(Author, related_name='books')
    genres = models.ManyToManyField(Genre, related_name='books')
    edition = models.CharField(max_length=50)
    page_count = models.IntegerField()
    total_copies = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    available_copies = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    cover_image = models.ImageField(upload_to=get_upload_path)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'books'
        verbose_name = 'book'

        constraints = [
            models.CheckConstraint(
                condition=Q(available_copies__gte=0),
                name='available_copies_non_negative'
        ), 
            models.CheckConstraint(
                condition=Q(available_copies__lte=F('total_copies')),
                name='available_lte_total'
            ),
    ]

    def __str__(self):
        return self.title
    
    def reduce_copies(self, requested):
        if requested <= 0:
            raise ValidationError("Requested quantity should be more than 0")
        if self.available_copies < requested:
            raise ValidationError(f"Quantity available {self.available_copies}")
        self.available_copies -= requested
        self.save()

    def clean(self):
        if self.available_copies > self.total_copies:
            raise ValidationError("Available copies can't exceed total copies")
        if self.total_copies < 0:
            raise ValidationError("Total copies can't be negative")

class BorrowRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrows')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True)
    return_date = models.DateTimeField(null=True)
    is_returned = models.BooleanField(default=False)

    class Meta:
        db_table = 'borrow_records'
        verbose_name = 'borrow_record'
        verbose_name_plural = 'borrow_records'

    def __str__(self):
        return f"{self.user.first_name} - {self.book.title}"
    
    def is_overdue(self):

        if self.is_returned == False and timezone.now() > self.due_date:
            return True
        return False
    
    def save(self, *args, **kwargs):

        if not self.id and not self.due_date:
            self.due_date = timezone.now() + datetime.timedelta(days=15)

        if self.return_date:
            self.is_returned = True

        super().save(*args, **kwargs)