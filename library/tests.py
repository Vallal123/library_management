from rest_framework.test import APITestCase
from .models import User, Book, Author, Genre

class BookListTestCase(APITestCase):
    """Test the /api/books/ endpoint"""
    
    def setUp(self):
        """Create test data"""
        # Create genre
        self.fiction = Genre.objects.create(name='Fiction')
        
        # Create author
        self.author = Author.objects.create(name='George Orwell')
        
        # Create books
        self.book1 = Book.objects.create(
            title='1984',
            isbn='isbn001',
            page_count=328,
            total_copies=5,
            available_copies=3,
            is_active=True  # Active book
        )
        self.book1.authors.add(self.author)
        self.book1.genres.add(self.fiction)
        
        self.book2 = Book.objects.create(
            title='Animal Farm',
            isbn='isbn002',
            page_count=141,
            total_copies=3,
            available_copies=0,
            is_active=False  # Inactive book (should not appear)
        )
    
    def test_list_books_success(self):
        """Test GET /api/books/ returns 200"""
        # Make request to /api/books/
        response = self.client.get('/api/books/')
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Check response has data
        self.assertIn('results', response.data)
        
        # Check active book appears
        titles = [book['title'] for book in response.data['results']]
        self.assertIn('1984', titles)
        
        # Check inactive book doesn't appear
        self.assertNotIn('Animal Farm', titles)
    
    def test_list_books_pagination(self):
        """Test pagination works at /api/books/?page=1"""
        response = self.client.get('/api/books/?page=1')
        
        self.assertEqual(response.status_code, 200)
        # DRF pagination returns these fields
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
    
    def test_list_books_with_page_size(self):
        """Test custom page size at /api/books/?page_size=5"""
        response = self.client.get('/api/books/?page_size=5')
        
        self.assertEqual(response.status_code, 200)
        # Should return at most 5 items
        self.assertLessEqual(len(response.data['results']), 5)


class UserRegisterTestCase(APITestCase):
    """Test the /api/register/ endpoint"""
    
    def test_register_success(self):
        """Test POST /api/register/ with valid data"""
        data = {
            'username': 'newuser',
            'password': 'secure123!',
            'email': 'newuser@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '9876543210',
            'address': 'Mumbai'
        }
        
        # Make POST request to /api/register/
        response = self.client.post('/api/register/', data)
        
        # Check status code
        self.assertEqual(response.status_code, 201)
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_register_duplicate_email(self):
        """Test POST /api/register/ with duplicate email"""
        # Create first user
        User.objects.create_user(
            username='user1',
            password='pass123',
            email='same@example.com'
        )
        
        # Try to register with same email
        data = {
            'username': 'user2',
            'password': 'pass123',
            'email': 'same@example.com',  # ← Duplicate
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone': '9876543210',
            'address': 'Delhi'
        }
        
        response = self.client.post('/api/register/', data)
        
        # Should fail
        self.assertEqual(response.status_code, 400)
        
        # Second user should NOT be created
        self.assertEqual(User.objects.filter(username='user2').count(), 0)
    
    def test_register_missing_field(self):
        """Test POST /api/register/ with missing required field"""
        data = {
            'username': 'newuser',
            'password': 'secure123!',
            # Missing email!
            'first_name': 'John',
        }
        
        response = self.client.post('/api/register/', data)
        
        # Should fail
        self.assertEqual(response.status_code, 400)


class UserLoginTestCase(APITestCase):
    """Test the /api/login/ endpoint"""
    
    def setUp(self):
        """Create test user"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def test_login_success(self):
        """Test POST /api/login/ with valid credentials"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        # Make POST request to /api/login/
        response = self.client.post('/api/login/', data)
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Check tokens in response
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_invalid_credentials(self):
        """Test POST /api/login/ with wrong password"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/api/login/', data)
        
        # Should fail
        self.assertEqual(response.status_code, 401)
        
        # Should have error message
        self.assertIn('detail', response.data)


class BorrowBookTestCase(APITestCase):
    """Test the /api/books/borrow/<book_id>/ endpoint"""
    
    def setUp(self):
        """Create test user and book"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn='isbn001',
            page_count=300,
            total_copies=5,
            available_copies=3
        )
    
    def test_borrow_success(self):
        """Test POST /api/books/borrow/1/ with auth"""
        # Login first
        self.client.force_authenticate(user=self.user)
        
        # Borrow book
        response = self.client.post(f'/api/books/borrow/{self.book.id}/')
        
        # Check status
        self.assertEqual(response.status_code, 201)
        
        # Check available copies reduced
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 2)
        
        # Check borrow record created
        from .models import BorrowRecord
        self.assertTrue(
            BorrowRecord.objects.filter(user=self.user, book=self.book).exists()
        )
    
    def test_borrow_no_copies(self):
        """Test borrow when no copies available"""
        # Set available copies to 0
        self.book.available_copies = 0
        self.book.save()
        
        # Try to borrow
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/books/borrow/{self.book.id}/')
        
        # Should fail
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
    
    def test_borrow_without_auth(self):
        """Test borrow without authentication"""
        # Don't login
        response = self.client.post(f'/api/books/borrow/{self.book.id}/')
        
        # Should fail (401 Unauthorized)
        self.assertEqual(response.status_code, 401)