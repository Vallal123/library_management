from django.contrib import admin

from .models import Author, Book, BorrowRecord, Genre, User


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('id', 'title', 'isbn', 'total_copies', 'available_copies', 'is_active')
    list_filter = ('is_active', 'genres', 'created_at')
    search_fields = ('title', 'isbn')
    filter_horizontal = ('authors', 'genres')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('date_joined',)
    list_display = ('first_name', 'email', 'is_active', 'date_joined')
    list_filter = ('is_active', 'date_joined')
    search_fields = ('name', 'email')


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    readonly_fields = ('borrow_date',)
    list_display = ('user', 'book', 'borrow_date', 'due_date', 'is_returned')
    list_filter = ('is_returned', 'borrow_date', 'due_date')
    search_fields = ('user__first_name', 'book__title')

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)