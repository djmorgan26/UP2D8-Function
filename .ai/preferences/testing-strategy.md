---
type: preference
category: testing
applies-to: all-projects
created: 2025-11-08
updated: 2025-11-08
---

# Personal Testing Strategy Preferences

**Purpose**: My preferred testing approaches across all projects.

**Usage**: Reference when writing tests. Document project-specific test setup in `.ai/knowledge/patterns/testing.md`.

---

## Testing Philosophy

### Core Beliefs

1. **Tests are documentation** - They show how code should be used
2. **Test behavior, not implementation** - Tests should survive refactoring
3. **Fast feedback** - Tests should run quickly and often
4. **Confidence over coverage** - 100% coverage != bug-free code
5. **Red-Green-Refactor** - Write failing test, make it pass, clean up

### Test Pyramid

```
        /\
       /  \      E2E (Few)
      /    \     - Critical user journeys
     /------\    - Slow, expensive
    /        \   Integration (Some)
   /          \  - API endpoints
  /            \ - Database operations
 /--------------\ Unit (Many)
                  - Business logic
                  - Utilities
                  - Fast, cheap
```

**Distribution**: ~70% unit, ~20% integration, ~10% E2E

---

## Unit Testing

### What to Unit Test

✅ **Always test**:
- Business logic functions
- Utility functions
- Data transformations
- Validation logic
- Error handling
- Edge cases

❌ **Don't unit test**:
- Framework code
- Third-party libraries
- Simple getters/setters
- Trivial assignments

### Unit Test Structure (AAA Pattern)

```typescript
describe('calculateDiscount', () => {
  it('should apply 10% discount for orders over $100', () => {
    // Arrange - Set up test data
    const orderTotal = 150;
    const customerType = 'regular';

    // Act - Execute the function
    const discount = calculateDiscount(orderTotal, customerType);

    // Assert - Verify the result
    expect(discount).toBe(15); // 10% of 150
  });
});
```

### Test Naming

**Format**: `should [expected behavior] when [condition]`

```typescript
// Good test names
it('should return user when ID exists')
it('should throw ValidationError when email is invalid')
it('should apply VIP discount when customer is premium member')

// Avoid vague names
it('works correctly')           // Too vague
it('test user creation')        // Not descriptive
it('returns something')         // What does it return?
```

### Mocking Philosophy

**Mock external dependencies, not internal logic**

```typescript
// Good: Mock external service
const mockEmailService = {
  send: jest.fn().mockResolvedValue({ success: true })
};

const userService = new UserService(mockEmailService);

// Bad: Mocking internal logic defeats the purpose
const mockCalculation = jest.fn().mockReturnValue(42);
// Now you're testing the mock, not your code!
```

**When to mock**:
- ✅ External APIs
- ✅ Database calls
- ✅ File system operations
- ✅ Date/time (for consistency)
- ✅ Random number generation

**When NOT to mock**:
- ❌ Internal functions (test them directly)
- ❌ Simple utilities
- ❌ Pure functions

---

## Integration Testing

### What to Integration Test

✅ **Test these integrations**:
- API endpoints (request → response)
- Database operations (query → result)
- Authentication flows
- Multiple services working together
- Data persistence and retrieval

### API Integration Test Example

```typescript
describe('POST /api/users', () => {
  beforeEach(async () => {
    // Set up test database
    await testDB.clean();
  });

  it('should create user and return 201', async () => {
    const userData = {
      email: 'test@example.com',
      name: 'Test User'
    };

    const response = await request(app)
      .post('/api/users')
      .send(userData)
      .expect(201);

    expect(response.body).toMatchObject({
      email: userData.email,
      name: userData.name
    });

    // Verify data persisted
    const user = await testDB.users.findByEmail(userData.email);
    expect(user).toBeDefined();
  });

  it('should return 400 for invalid email', async () => {
    const invalidData = {
      email: 'not-an-email',
      name: 'Test'
    };

    const response = await request(app)
      .post('/api/users')
      .send(invalidData)
      .expect(400);

    expect(response.body.error).toBe('Validation failed');
  });
});
```

### Database Testing

**Use test database**:
```typescript
// Setup
beforeAll(async () => {
  await testDB.connect('test_database');
});

beforeEach(async () => {
  await testDB.clean(); // Clear all tables
});

afterAll(async () => {
  await testDB.disconnect();
});
```

**Test transactions**:
```typescript
it('should rollback on error', async () => {
  const userId = await createUser({ email: 'test@example.com' });

  await expect(
    updateUserWithInvalidData(userId)
  ).rejects.toThrow();

  // Verify original data still exists (transaction rolled back)
  const user = await getUser(userId);
  expect(user.email).toBe('test@example.com');
});
```

---

## End-to-End (E2E) Testing

### When to Write E2E Tests

**Critical user journeys only**:
- User registration → login → main action → logout
- Purchase flow: browse → add to cart → checkout → payment
- Admin workflows: login → create resource → verify

**Don't E2E test**:
- Every edge case (use unit tests)
- Every validation (use integration tests)
- UI variations (use component tests)

### E2E Test Example

```typescript
describe('User Registration Flow', () => {
  it('should allow new user to register and login', async () => {
    // Navigate to registration
    await page.goto('/register');

    // Fill form
    await page.fill('[name=email]', 'newuser@example.com');
    await page.fill('[name=password]', 'SecurePass123!');
    await page.fill('[name=confirmPassword]', 'SecurePass123!');

    // Submit
    await page.click('button[type=submit]');

    // Verify redirect to welcome page
    await page.waitForURL('/welcome');
    expect(await page.textContent('h1')).toContain('Welcome');

    // Logout
    await page.click('[data-testid=logout]');

    // Login again
    await page.goto('/login');
    await page.fill('[name=email]', 'newuser@example.com');
    await page.fill('[name=password]', 'SecurePass123!');
    await page.click('button[type=submit]');

    // Verify successful login
    await page.waitForURL('/dashboard');
    expect(await page.isVisible('[data-testid=user-menu]')).toBe(true);
  });
});
```

---

## Test Data Management

### Test Data Strategy

**Option 1: Factories** (Preferred for flexibility)
```typescript
// user.factory.ts
export function createUserData(overrides = {}) {
  return {
    email: `test-${Date.now()}@example.com`,
    name: 'Test User',
    role: 'user',
    ...overrides
  };
}

// Usage
const admin = createUserData({ role: 'admin' });
const specificEmail = createUserData({ email: 'specific@example.com' });
```

**Option 2: Fixtures** (Good for complex scenarios)
```typescript
// fixtures/users.json
{
  "regularUser": {
    "email": "regular@example.com",
    "name": "Regular User",
    "role": "user"
  },
  "adminUser": {
    "email": "admin@example.com",
    "name": "Admin User",
    "role": "admin"
  }
}

// Usage
import users from './fixtures/users.json';
await createUser(users.adminUser);
```

### Test Database Seeds

```typescript
async function seedTestData() {
  // Create test users
  const user1 = await createUser(createUserData({ email: 'user1@test.com' }));
  const user2 = await createUser(createUserData({ email: 'user2@test.com' }));

  // Create test orders
  await createOrder({ userId: user1.id, total: 100 });
  await createOrder({ userId: user2.id, total: 200 });

  return { user1, user2 };
}

// Usage in tests
beforeEach(async () => {
  await testDB.clean();
  testData = await seedTestData();
});
```

---

## Test Coverage

### Coverage Targets

| Code Type | Minimum | Target |
|-----------|---------|--------|
| Critical business logic | 95% | 100% |
| API endpoints | 90% | 95% |
| Services | 85% | 90% |
| Utilities | 80% | 90% |
| UI components | 70% | 80% |

### What Coverage Doesn't Mean

- ❌ 100% coverage ≠ bug-free
- ❌ Coverage ≠ quality
- ❌ High coverage ≠ good tests

**Focus on**:
- ✅ Testing behavior
- ✅ Edge cases covered
- ✅ Error paths tested
- ✅ Business rules verified

---

## Test Organization

### File Structure

```
src/
├── features/
│   ├── users/
│   │   ├── user.service.ts
│   │   ├── user.service.test.ts     # Unit tests
│   │   ├── user.controller.ts
│   │   ├── user.controller.test.ts   # Unit tests
│   │   └── user.integration.test.ts  # Integration tests
│   └── auth/
│       ├── auth.service.ts
│       └── auth.service.test.ts

tests/
├── e2e/                               # E2E tests
│   ├── user-registration.e2e.test.ts
│   └── checkout-flow.e2e.test.ts
├── fixtures/                          # Test data
│   ├── users.json
│   └── orders.json
└── helpers/                           # Test utilities
    ├── test-db.ts
    └── factories.ts
```

### Naming Conventions

- Unit tests: `*.test.ts` or `*.spec.ts`
- Integration tests: `*.integration.test.ts`
- E2E tests: `*.e2e.test.ts`

---

## Assertions

### Preferred Matchers

```typescript
// Equality
expect(value).toBe(5);              // Primitive equality
expect(object).toEqual({ a: 1 });   // Deep equality
expect(value).not.toBe(null);       // Negation

// Truthiness
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();

// Numbers
expect(value).toBeGreaterThan(10);
expect(value).toBeLessThanOrEqual(100);
expect(0.1 + 0.2).toBeCloseTo(0.3); // Floating point

// Strings
expect(text).toContain('substring');
expect(email).toMatch(/.*@.*\..*/);

// Arrays
expect(array).toHaveLength(3);
expect(array).toContain(item);
expect(array).toEqual(expect.arrayContaining([1, 2]));

// Objects
expect(object).toHaveProperty('key');
expect(object).toMatchObject({ a: 1 }); // Partial match

// Exceptions
expect(() => fn()).toThrow();
expect(() => fn()).toThrow(ValidationError);
expect(() => fn()).toThrow('Invalid email');

// Async
await expect(promise).resolves.toBe(value);
await expect(promise).rejects.toThrow();
```

---

## Testing Patterns

### Testing Async Code

```typescript
// Async/await (preferred)
it('should fetch user', async () => {
  const user = await getUser('123');
  expect(user.id).toBe('123');
});

// Promises with resolves/rejects
it('should fetch user', () => {
  return expect(getUser('123')).resolves.toMatchObject({ id: '123' });
});
```

### Testing Error Cases

```typescript
it('should handle errors', async () => {
  // Setup mock to throw
  mockDB.findUser.mockRejectedValue(new Error('DB error'));

  // Test that error is handled
  await expect(userService.getUser('123'))
    .rejects
    .toThrow('DB error');
});
```

### Testing with Timers

```typescript
beforeEach(() => {
  jest.useFakeTimers();
});

afterEach(() => {
  jest.useRealTimers();
});

it('should retry after delay', async () => {
  const promise = retryOperation();

  // Fast-forward time
  jest.advanceTimersByTime(5000);

  await expect(promise).resolves.toBe(expectedValue);
});
```

---

## Test Performance

### Keep Tests Fast

✅ **Do**:
- Use in-memory databases for tests
- Mock slow external services
- Run tests in parallel
- Use test.only during development (remove before commit)

❌ **Don't**:
- Make real API calls in tests
- Use sleep/wait unnecessarily
- Load large datasets
- Run E2E tests in unit test suite

### Measuring Test Speed

```bash
# Show slowest tests
npm test -- --verbose --detectSlowTests

# Run with timing
npm test -- --testTimeout=5000
```

---

## Continuous Integration

### CI Test Strategy

```yaml
# Example: .github/workflows/test.yml
- name: Unit Tests
  run: npm run test:unit
  timeout-minutes: 5

- name: Integration Tests
  run: npm run test:integration
  timeout-minutes: 10

- name: E2E Tests
  run: npm run test:e2e
  if: github.ref == 'refs/heads/main'
  timeout-minutes: 15
```

**Strategy**:
1. Run unit tests on every commit (fast feedback)
2. Run integration tests on every PR
3. Run E2E tests on main branch only (slower, less frequent)

---

## TDD (Test-Driven Development)

### When I Use TDD

✅ **Good for TDD**:
- Complex business logic
- Algorithms with clear inputs/outputs
- Bug fixes (write failing test first)
- Refactoring (tests ensure behavior unchanged)

❌ **Skip TDD**:
- Exploratory coding (spike solutions)
- UI prototypes
- Simple CRUD operations
- One-off scripts

### TDD Cycle

```
1. Red   - Write failing test
2. Green - Write minimal code to pass
3. Refactor - Clean up while keeping tests green
4. Repeat
```

---

## Common Testing Anti-Patterns

### ❌ Testing Implementation Details

```typescript
// BAD: Testing internal state
expect(service['privateField']).toBe(5);

// GOOD: Testing behavior
expect(service.getValue()).toBe(5);
```

### ❌ Fragile Tests

```typescript
// BAD: Dependent on execution order
describe('User tests', () => {
  let createdUserId;

  it('creates user', async () => {
    createdUserId = await createUser();
  });

  it('updates user', async () => {
    await updateUser(createdUserId); // Fails if previous test fails!
  });
});

// GOOD: Independent tests
describe('User tests', () => {
  it('creates user', async () => {
    const userId = await createUser();
    expect(userId).toBeDefined();
  });

  it('updates user', async () => {
    const userId = await createUser(); // Own setup
    await updateUser(userId);
  });
});
```

### ❌ One Assertion Per Test (Too Strict)

```typescript
// Acceptable: Multiple related assertions
it('should create user with correct properties', () => {
  const user = createUser({ email: 'test@example.com', name: 'Test' });

  expect(user.email).toBe('test@example.com');
  expect(user.name).toBe('Test');
  expect(user.id).toBeDefined();
  expect(user.createdAt).toBeInstanceOf(Date);
});
```

---

## Project-Specific Testing Setup

Document in `.ai/knowledge/patterns/testing.md`:

- Test framework setup (Jest, Vitest, etc.)
- Test database configuration
- Mock/stub patterns specific to this project
- CI/CD test pipeline
- Coverage thresholds
- Test data management approach

---

Updated: 2025-11-08
