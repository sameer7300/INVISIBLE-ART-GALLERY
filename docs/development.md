# Invisible Art Gallery - Development Guide

This document outlines the development process, coding standards, and best practices for contributing to the Invisible Art Gallery project.

## Development Workflow

### Git Workflow

We follow a Git Flow-inspired workflow:

1. `main` branch: Production-ready code
2. `develop` branch: Integration branch for features
3. Feature branches: Named `feature/feature-name`
4. Bugfix branches: Named `bugfix/bug-description`

```
main
 ↑
develop
 ↑
feature/user-profiles
```

### Setting Up for Development

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/invisible-art-gallery.git
   cd invisible-art-gallery
   ```

2. Create a feature branch:
   ```bash
   git checkout develop
   git checkout -b feature/your-feature-name
   ```

3. Make your changes, following the coding standards below

4. Commit your changes with meaningful messages:
   ```bash
   git commit -m "feat: add user profile image upload"
   ```

5. Push your branch and create a pull request against `develop`

### Pull Request Process

1. Ensure all tests pass
2. Request a code review from at least one team member
3. Address any feedback from reviewers
4. Squash commits if necessary
5. Merge using "Squash and merge" option

## Coding Standards

### Python (Django) Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with a few exceptions:

- Maximum line length of 100 characters
- Use 4 spaces for indentation
- Use docstrings for all public modules, functions, classes, and methods
- Use type hints for function signatures

Example:
```python
def encrypt_artwork(file_data: bytes, key: str) -> bytes:
    """
    Encrypt artwork data using the provided key.
    
    Args:
        file_data: Raw binary data of the artwork
        key: Encryption key to use
        
    Returns:
        Encrypted binary data
    """
    # Implementation here
    return encrypted_data
```

### JavaScript (React) Style Guide

We follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript) with a few adjustments:

- Use functional components with hooks instead of class components
- Use TypeScript for type checking
- Use CSS-in-JS with styled-components
- Prefer async/await over promises

Example:
```jsx
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { fetchArtwork } from '../../services/api';

const ArtworkContainer = styled.div`
  display: flex;
  flex-direction: column;
  padding: 1rem;
  border-radius: 4px;
  background-color: ${props => props.theme.colors.background};
`;

type ArtworkProps = {
  id: string;
};

const Artwork: React.FC<ArtworkProps> = ({ id }) => {
  const [artwork, setArtwork] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const loadArtwork = async () => {
      try {
        const data = await fetchArtwork(id);
        setArtwork(data);
      } catch (error) {
        console.error('Failed to load artwork:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadArtwork();
  }, [id]);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <ArtworkContainer>
      <h2>{artwork.title}</h2>
      <p>{artwork.description}</p>
      {/* More artwork display logic */}
    </ArtworkContainer>
  );
};

export default Artwork;
```

## Testing

### Backend Testing

- Use Django's test framework
- Aim for 80% code coverage minimum
- Write unit tests for models, services, and views
- Write integration tests for API endpoints

Example:
```python
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Artwork
from accounts.models import User

class ArtworkAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testartist',
            email='artist@example.com',
            password='testpassword',
            is_artist=True
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_artwork(self):
        data = {
            'title': 'Test Artwork',
            'description': 'A test artwork',
            'reveal_conditions': {'type': 'view_count', 'value': 10}
        }
        response = self.client.post('/api/v1/artworks/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Artwork.objects.count(), 1)
        self.assertEqual(Artwork.objects.get().title, 'Test Artwork')
```

### Frontend Testing

- Use Jest and React Testing Library
- Write unit tests for components, hooks, and utilities
- Write integration tests for complex components
- Use snapshots sparingly

Example:
```jsx
import { render, screen, waitFor } from '@testing-library/react';
import Artwork from './Artwork';
import { fetchArtwork } from '../../services/api';

jest.mock('../../services/api');

describe('Artwork Component', () => {
  it('renders loading state initially', () => {
    fetchArtwork.mockResolvedValueOnce({
      id: '123',
      title: 'Test Artwork',
      description: 'A test artwork'
    });
    
    render(<Artwork id="123" />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
  
  it('renders artwork data after loading', async () => {
    fetchArtwork.mockResolvedValueOnce({
      id: '123',
      title: 'Test Artwork',
      description: 'A test artwork'
    });
    
    render(<Artwork id="123" />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Artwork')).toBeInTheDocument();
      expect(screen.getByText('A test artwork')).toBeInTheDocument();
    });
  });
});
```

## Documentation

### Code Documentation

- Use descriptive variable and function names
- Add comments for complex logic
- Use docstrings for classes and functions
- Keep documentation updated when code changes

### API Documentation

- Document all API endpoints
- Include request and response formats
- Document authentication requirements
- Use OpenAPI/Swagger for auto-generated docs

## Security Best Practices

- Never commit secrets or credentials
- Use environment variables for configuration
- Validate all user inputs
- Use parameterized queries to prevent SQL injection
- Implement proper authorization checks
- Follow OWASP security guidelines

## Performance Considerations

- Use database indexes for frequently queried fields
- Optimize database queries (use `select_related` and `prefetch_related`)
- Implement caching for expensive operations
- Paginate API results
- Use lazy loading for images and components

## Deployment Process

Development builds are automatically deployed to the staging environment when merged to `develop`. Production deployments require approval and are triggered by releases to `main`.

1. Create a release branch from `develop`
2. Run the full test suite
3. Merge to `main` after approval
4. Tag the release with semantic versioning

```bash
git checkout develop
git pull
git checkout -b release/1.2.0
# Run tests and verify
git checkout main
git merge release/1.2.0
git tag -a v1.2.0 -m "Version 1.2.0"
git push origin main --tags
```

## Libraries and Tools

### Backend
- Django 4.2+
- Django REST Framework
- Django Channels
- Cryptography
- Celery (for background tasks)
- pytest (for testing)

### Frontend
- React 18+
- TypeScript
- Styled Components
- React Query (for data fetching)
- React Router
- Axios
- Jest and React Testing Library 