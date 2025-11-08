---
type: preference
category: coding-standards
applies-to: all-projects
created: 2025-11-08
updated: 2025-11-08
---

# Personal Coding Standards

**Purpose**: My preferred coding conventions that apply across all projects.

**Usage**: Reference this when building features. Project-specific variations should be documented in `.ai/knowledge/patterns/`.

---

## General Principles

### Code Quality
- **Readability over cleverness** - Code is read 10x more than written
- **Single Responsibility** - Functions/classes do one thing well
- **DRY (Don't Repeat Yourself)** - But don't over-abstract prematurely
- **YAGNI (You Aren't Gonna Need It)** - Build what's needed now, not what might be needed

### Comments
- **Why, not what** - Code shows what, comments explain why
- **Document non-obvious decisions** - Future you needs context
- **Keep comments current** - Outdated comments are worse than no comments
- **Prefer self-documenting code** - Good names > excessive comments

---

## Naming Conventions

### Variables
- **Descriptive names**: `userCount` not `uc`, `emailAddress` not `ea`
- **Boolean prefix**: `isActive`, `hasPermission`, `canEdit`
- **Avoid abbreviations**: Unless industry standard (`id`, `url`, `api`)

### Functions
- **Verb-based**: `getUser()`, `saveData()`, `calculateTotal()`
- **Specific, not generic**: `validateEmailFormat()` not `validate()`
- **Length proportional to scope**: Short names for small scopes, descriptive for public APIs

### Files
- **kebab-case**: `user-service.ts`, `auth-middleware.ts`
- **Purpose-based**: `user-repository.ts` not `users.ts`
- **Co-locate related**: Tests next to source when possible

### Classes/Types
- **PascalCase**: `UserService`, `AuthenticationError`
- **Noun-based**: Represent things, not actions
- **Interfaces**: `IUserRepository` or just `UserRepository` (depending on language)

---

## Code Organization

### File Structure
```
src/
├── features/           # Feature-based organization
│   ├── auth/
│   │   ├── auth.service.ts
│   │   ├── auth.controller.ts
│   │   └── auth.test.ts
│   └── users/
│       ├── user.service.ts
│       ├── user.repository.ts
│       └── user.test.ts
├── shared/             # Shared utilities
│   ├── errors/
│   ├── middleware/
│   └── utils/
└── config/             # Configuration
```

### Import Order
1. External dependencies (Node.js, npm packages)
2. Internal modules (from this project)
3. Relative imports (same directory)

```typescript
// External
import { Request, Response } from 'express';
import * as jwt from 'jsonwebtoken';

// Internal
import { UserService } from '@/features/users';
import { AuthError } from '@/shared/errors';

// Relative
import { validateToken } from './utils';
```

---

## Error Handling

### Preferred Pattern
- **Explicit error handling** - Don't swallow errors silently
- **Custom error classes** - Extend base Error with context
- **Fail fast** - Validate inputs early, throw meaningful errors
- **Log with context** - Include relevant data for debugging

### Example
```typescript
class ValidationError extends Error {
  constructor(message: string, public field: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

function validateEmail(email: string): void {
  if (!email || !email.includes('@')) {
    throw new ValidationError('Invalid email format', 'email');
  }
}
```

---

## Testing

### Test Philosophy
- **Test behavior, not implementation** - Tests should survive refactoring
- **AAA Pattern**: Arrange, Act, Assert
- **One assertion focus per test** - Multiple assertions OK if testing same concept
- **Descriptive test names**: `it('should throw error when email is invalid')`

### Coverage Targets
- **Critical paths**: 100% coverage
- **Business logic**: 90%+ coverage
- **Utilities**: 80%+ coverage
- **UI components**: 70%+ coverage (focus on logic, not rendering)

### Test Organization
```typescript
describe('UserService', () => {
  describe('createUser()', () => {
    it('should create user with valid data', () => {
      // Arrange
      const userData = { email: 'test@example.com', name: 'Test' };

      // Act
      const user = userService.createUser(userData);

      // Assert
      expect(user.email).toBe('test@example.com');
    });

    it('should throw error when email is invalid', () => {
      // Arrange
      const userData = { email: 'invalid', name: 'Test' };

      // Act & Assert
      expect(() => userService.createUser(userData))
        .toThrow(ValidationError);
    });
  });
});
```

---

## Dependency Management

### Injection Pattern
- **Prefer constructor injection** - Makes dependencies explicit
- **Use interfaces** - Depend on abstractions, not concretions
- **Avoid service locators** - Pass dependencies, don't fetch them

```typescript
// Good
class UserService {
  constructor(
    private userRepository: IUserRepository,
    private emailService: IEmailService
  ) {}
}

// Avoid
class UserService {
  private userRepository = Container.get(UserRepository);
}
```

---

## Security Practices

### Always
- ✅ Validate all inputs
- ✅ Sanitize outputs (prevent XSS)
- ✅ Use parameterized queries (prevent SQL injection)
- ✅ Hash passwords (never store plaintext)
- ✅ Use HTTPS in production
- ✅ Keep dependencies updated

### Never
- ❌ Commit secrets to git
- ❌ Trust user input
- ❌ Use `eval()` or similar
- ❌ Expose sensitive data in errors
- ❌ Disable security features "temporarily"

---

## Performance Considerations

### Optimize When Needed
- **Profile before optimizing** - Don't guess, measure
- **Optimize hot paths** - Focus on code that runs frequently
- **Readability first** - Until performance becomes an issue

### Common Patterns
- **Lazy loading** - Load resources when needed
- **Caching** - Cache expensive operations (with invalidation strategy)
- **Batch operations** - Group database/API calls when possible
- **Async operations** - Don't block on I/O

---

## Git Practices

### Commits
- **Atomic commits** - One logical change per commit
- **Conventional commits**: `feat:`, `fix:`, `docs:`, `refactor:`, etc.
- **Descriptive messages**: What and why, not just what
- **Present tense**: "Add feature" not "Added feature"

### Branches
- **Feature branches**: `feature/user-authentication`
- **Bug fixes**: `fix/login-validation`
- **Short-lived**: Merge within 1-3 days when possible

---

## Documentation

### Code Documentation
- **Public APIs**: Always document
- **Complex algorithms**: Explain approach
- **Non-obvious code**: Add comments
- **TODOs**: Include context and ticket number

### README Files
Every project should have:
- What it does (1-2 sentences)
- How to install/setup
- How to run
- How to test
- How to contribute (if applicable)

---

## Language-Specific Preferences

### TypeScript
- **Strict mode enabled** - `strict: true` in tsconfig.json
- **Explicit types** - Especially for public APIs
- **Avoid `any`** - Use `unknown` if type truly unknown
- **Interfaces over types** - For object shapes

### JavaScript
- **Use modern syntax** - ES6+ features
- **Const by default** - Use `let` only when reassignment needed
- **Arrow functions** - For callbacks and short functions
- **Template literals** - Over string concatenation

### Python
- **PEP 8 compliant** - Use black/flake8 for formatting
- **Type hints** - For function signatures
- **Docstrings** - Google/NumPy style
- **Virtual environments** - Always use venv/poetry

---

## Tooling Preferences

### Formatters
- **Automated formatting** - Prettier, Black, etc.
- **On save** - Format on every save
- **No manual formatting** - Let tools handle it

### Linters
- **Strict rules** - ESLint, Pylint with strict configs
- **Pre-commit hooks** - Catch issues before commit
- **CI/CD integration** - Fail builds on lint errors

### IDEs
- **Consistent configuration** - Share .editorconfig, .vscode settings
- **Extensions**: Linters, formatters, type checkers

---

## When to Deviate

These are **preferences, not laws**. Deviate when:

1. **Project conventions differ** - Team consensus > personal preference
2. **Framework patterns differ** - Follow framework idioms
3. **Performance critical** - Optimization may require less readable code
4. **Legacy codebase** - Match existing patterns for consistency

**Document deviations** in `.ai/knowledge/patterns/` with rationale.

---

## Updating These Preferences

These preferences evolve as I learn. Updates should:
- Be intentional (not reactions to one-off situations)
- Apply broadly (not project-specific)
- Have clear rationale (explain why)

Updated: 2025-11-08
