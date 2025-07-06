# Testing Guide

## Overview

This guide covers testing strategies, setup, and execution for the Design Gallery FastAPI backend.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py               # Pytest configuration and fixtures
├── test_auth.py             # Authentication tests
├── test_designs.py          # Design management tests
├── test_admin.py            # Admin functionality tests
├── test_upload.py           # File upload tests
├── unit/                    # Unit tests
│   ├── test_models.py       # Pydantic model tests
│   ├── test_services.py     # Service layer tests
│   └── test_utils.py        # Utility function tests
└── integration/             # Integration tests
    ├── test_database.py     # Database integration
    ├── test_storage.py      # R2 storage integration
    └── test_api_flow.py     # End-to-end API flows
```

## Setup

### Install Test Dependencies

```bash
pip install pytest pytest-asyncio pytest-httpx pytest-mock
```

### Environment Configuration

Create `.env.test`:

```bash
ENVIRONMENT=test
DEBUG=true
JWT_SECRET=test-secret-key-for-testing-only
CLOUDFLARE_ACCOUNT_ID=test-account
CLOUDFLARE_D1_DATABASE_ID=test-db-id
CLOUDFLARE_API_TOKEN=test-token
CLOUDFLARE_R2_ACCOUNT_ID=test-r2-account
CLOUDFLARE_R2_ACCESS_KEY=test-access-key
CLOUDFLARE_R2_SECRET_KEY=test-secret-key
CLOUDFLARE_R2_BUCKET_NAME=test-bucket
CLOUDFLARE_R2_PUBLIC_URL=https://test-r2.dev
```

## Test Categories

### Unit Tests

Test individual components in isolation:

```python
# tests/unit/test_models.py
import pytest
from app.models.user import UserCreate, UserResponse

def test_user_create_model():
    """Test user creation model validation."""
    user_data = {
        "username": "testuser",
        "password": "password123"
    }
    user = UserCreate(**user_data)
    assert user.username == "testuser"
    assert user.password == "password123"

def test_user_create_validation():
    """Test user creation validation rules."""
    with pytest.raises(ValueError):
        UserCreate(username="ab", password="123")  # Too short
```

### Integration Tests

Test component interactions:

```python
# tests/integration/test_auth_flow.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_auth_flow():
    """Test complete authentication flow."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user
        register_response = await client.post("/api/auth/register", json={
            "username": "testuser",
            "password": "password123"
        })
        assert register_response.status_code == 200
        
        # Login should fail (user not approved)
        login_response = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "password123"
        })
        assert login_response.status_code == 403
```

### End-to-End Tests

Test complete user workflows:

```python
# tests/test_complete_workflow.py
@pytest.mark.asyncio
async def test_design_management_workflow():
    """Test complete design management workflow."""
    # 1. Admin login
    # 2. Upload image
    # 3. Create design
    # 4. User login
    # 5. View design
    # 6. Add to favorites
    # 7. Admin update design
    # 8. Verify changes
```

## Running Tests

### All Tests

```bash
pytest
```

### Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/test_auth.py

# Specific test function
pytest tests/test_auth.py::test_user_registration
```

### Coverage Reports

```bash
# Run with coverage
pytest --cov=app

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Coverage with missing lines
pytest --cov=app --cov-report=term-missing
```

## Test Configuration

### pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --asyncio-mode=auto
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### Fixtures

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def client():
    """Test client fixture."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def admin_token():
    """Admin authentication token."""
    # Create admin user and return token
    return "admin-jwt-token"

@pytest.fixture
async def user_token():
    """Regular user authentication token."""
    # Create regular user and return token
    return "user-jwt-token"
```

## Mocking External Services

### Mock Cloudflare D1

```python
# tests/mocks/test_database.py
from unittest.mock import AsyncMock, patch

@patch('app.core.database.CloudflareD1Client.execute_query')
async def test_user_creation_with_mock_db(mock_query):
    """Test user creation with mocked database."""
    mock_query.return_value = {
        "results": [{"id": 1, "username": "testuser"}]
    }
    
    # Test user service
    result = await UserService.create_user(user_data)
    assert result.id == 1
```

### Mock Cloudflare R2

```python
@patch('app.core.storage.R2StorageManager.upload_file')
async def test_image_upload_with_mock_r2(mock_upload):
    """Test image upload with mocked R2."""
    mock_upload.return_value = True
    
    # Test upload
    result = await storage_manager.upload_file(file_data, "test.jpg")
    assert result is True
```

## Performance Testing

### Load Testing with pytest-benchmark

```python
import pytest

def test_password_hashing_performance(benchmark):
    """Test password hashing performance."""
    result = benchmark(security_manager.hash_password, "password123")
    assert result is not None
```

### API Performance Tests

```python
@pytest.mark.asyncio
async def test_api_response_time():
    """Test API response times."""
    import time
    
    start_time = time.time()
    response = await client.get("/api/designs")
    response_time = time.time() - start_time
    
    assert response.status_code == 200
    assert response_time < 1.0  # Under 1 second
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Test Data Management

### Test Database Setup

```python
@pytest.fixture(scope="session")
async def test_db():
    """Set up test database."""
    # Create test database
    # Run migrations
    # Yield database
    # Cleanup
```

### Test Data Factories

```python
# tests/factories.py
import factory
from app.models.user import UserCreate

class UserFactory(factory.Factory):
    class Meta:
        model = UserCreate
    
    username = factory.Sequence(lambda n: f"user{n}")
    password = "password123"

class DesignFactory(factory.Factory):
    class Meta:
        model = DesignCreate
    
    title = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text')
    category = factory.Faker('word')
```

## Best Practices

### Test Organization

1. **One assertion per test** when possible
2. **Descriptive test names** that explain what is being tested
3. **Arrange-Act-Assert** pattern
4. **Independent tests** that don't rely on each other

### Test Data

1. **Use factories** for test data generation
2. **Cleanup after tests** to avoid state pollution
3. **Use realistic data** that matches production patterns

### Async Testing

```python
@pytest.mark.asyncio
async def test_async_function():
    """Proper async test structure."""
    # Arrange
    data = {"key": "value"}
    
    # Act
    result = await async_function(data)
    
    # Assert
    assert result is not None
```

## Debugging Tests

### Running Specific Tests

```bash
# Run with verbose output
pytest -v tests/test_auth.py

# Run with debug output
pytest -s tests/test_auth.py

# Stop on first failure
pytest -x tests/

# Drop into debugger on failure
pytest --pdb tests/
```

### Test Coverage Analysis

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## Common Test Patterns

### Testing API Endpoints

```python
async def test_get_designs_authenticated():
    """Test getting designs with authentication."""
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await client.get("/api/designs", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "designs" in data
    assert isinstance(data["designs"], list)
```

### Testing Error Conditions

```python
async def test_invalid_authentication():
    """Test API with invalid authentication."""
    headers = {"Authorization": "Bearer invalid-token"}
    response = await client.get("/api/designs", headers=headers)
    
    assert response.status_code == 401
    assert "error" in response.json()
```

### Testing Input Validation

```python
async def test_user_registration_validation():
    """Test user registration input validation."""
    invalid_data = {"username": "ab", "password": "123"}
    response = await client.post("/api/auth/register", json=invalid_data)
    
    assert response.status_code == 422
    errors = response.json()["details"]
    assert any("username" in str(error) for error in errors)
```

## Continuous Integration

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        types: [python]
        pass_filenames: false
```

### Quality Gates

1. **Code Coverage**: Minimum 80% coverage
2. **Test Pass Rate**: 100% tests must pass
3. **Performance**: API response times under thresholds
4. **Security**: No known vulnerabilities in dependencies

## Troubleshooting

### Common Issues

1. **Async test failures**: Ensure proper `@pytest.mark.asyncio` usage
2. **Database connection errors**: Check test environment configuration
3. **Import errors**: Verify PYTHONPATH and module structure
4. **Flaky tests**: Review test isolation and cleanup

### Test Environment Setup

```bash
# Reset test environment
python -m pytest --cache-clear

# Rebuild test database
python scripts/setup_test_db.py

# Clear test data
python scripts/cleanup_test_data.py
``` 