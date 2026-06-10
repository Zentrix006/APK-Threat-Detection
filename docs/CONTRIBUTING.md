# Contributing to APK Threat Intelligence Platform

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others succeed

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/apk-threat-detection.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Push to your fork and create a Pull Request

## Development Workflow

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Format code
black app/

# Lint
flake8 app/

# Run tests
pytest

# Run server
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev

# Format code
npm run format

# Lint
npm run lint
```

## Code Standards

### Python (Backend)
- Follow PEP 8
- Use type hints
- Write docstrings
- Format with Black
- Lint with Flake8

### TypeScript/JavaScript (Frontend)
- Use TypeScript for new files
- Follow ESLint rules
- Use Prettier for formatting
- Comment complex logic

## Commit Messages

Use clear, concise commit messages:
```
feat: Add APK upload functionality
fix: Resolve database connection issue
docs: Update API documentation
test: Add analysis tests
style: Format code
refactor: Reorganize database models
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Provide clear PR description
6. Request review from maintainers

## Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

## Documentation

- Update README.md for user-facing changes
- Update API.md for API changes
- Add docstrings to functions
- Comment complex algorithms
- Include examples for new features

## Reporting Bugs

Use GitHub Issues with:
- Clear title
- Detailed description
- Steps to reproduce
- Expected vs actual behavior
- Environment info (OS, Python version, etc.)
- Screenshots if applicable

## Feature Requests

Include:
- Clear description of the feature
- Use cases and benefits
- Proposed implementation (optional)
- Related issues or discussions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Open a GitHub Discussion or contact the maintainers.

Thank you for contributing! 🙏
