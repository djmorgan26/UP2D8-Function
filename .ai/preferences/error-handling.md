---
type: preference
category: error-handling
applies-to: all-projects
created: 2025-11-08
updated: 2025-11-08
---

# Personal Error Handling Preferences

**Purpose**: My preferred approaches to error handling across all projects.

**Usage**: Reference when implementing error handling. Document project-specific implementations in `.ai/knowledge/patterns/error-handling.md`.

---

## Core Philosophy

### Principles
1. **Fail fast** - Detect errors early, report immediately
2. **Be explicit** - Don't hide errors or swallow exceptions
3. **Provide context** - Include enough information to debug
4. **User-friendly** - Show helpful messages to users, detailed logs for developers
5. **Recover when possible** - But don't hide failures

---

## Error Classification

### Error Types I Use

#### 1. Validation Errors
**When**: Invalid input from users or external systems
**Response**: 400 Bad Request, clear message about what's wrong
**Recovery**: None - user must fix input

```typescript
class ValidationError extends Error {
  constructor(
    message: string,
    public field: string,
    public value?: any
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}
```

#### 2. Not Found Errors
**When**: Requested resource doesn't exist
**Response**: 404 Not Found
**Recovery**: None - resource doesn't exist

```typescript
class NotFoundError extends Error {
  constructor(
    public resourceType: string,
    public identifier: string
  ) {
    super(`${resourceType} not found: ${identifier}`);
    this.name = 'NotFoundError';
  }
}
```

#### 3. Authorization Errors
**When**: User lacks permission
**Response**: 403 Forbidden
**Recovery**: None - user needs permission granted

```typescript
class AuthorizationError extends Error {
  constructor(
    public action: string,
    public resource: string
  ) {
    super(`Not authorized to ${action} ${resource}`);
    this.name = 'AuthorizationError';
  }
}
```

#### 4. Authentication Errors
**When**: Invalid or missing credentials
**Response**: 401 Unauthorized
**Recovery**: User must authenticate

```typescript
class AuthenticationError extends Error {
  constructor(message: string = 'Authentication required') {
    super(message);
    this.name = 'AuthenticationError';
  }
}
```

#### 5. Business Logic Errors
**When**: Operation violates business rules
**Response**: 422 Unprocessable Entity
**Recovery**: Depends on context

```typescript
class BusinessRuleError extends Error {
  constructor(
    message: string,
    public rule: string
  ) {
    super(message);
    this.name = 'BusinessRuleError';
  }
}
```

#### 6. External Service Errors
**When**: Dependency (API, database, etc.) fails
**Response**: 503 Service Unavailable or 500 Internal Server Error
**Recovery**: Retry with backoff, fallback, or fail

```typescript
class ExternalServiceError extends Error {
  constructor(
    public service: string,
    message: string,
    public originalError?: Error
  ) {
    super(`${service} error: ${message}`);
    this.name = 'ExternalServiceError';
  }
}
```

#### 7. Unexpected Errors
**When**: Something truly unexpected happens
**Response**: 500 Internal Server Error
**Recovery**: Log, alert, fail gracefully

---

## Error Handling Patterns

### Pattern 1: Input Validation (Eager)

**Validate early, throw immediately:**

```typescript
function createUser(email: string, name: string) {
  // Validate ALL inputs first
  if (!email || !email.includes('@')) {
    throw new ValidationError('Invalid email format', 'email', email);
  }

  if (!name || name.trim().length === 0) {
    throw new ValidationError('Name is required', 'name', name);
  }

  if (name.length > 100) {
    throw new ValidationError('Name too long (max 100 chars)', 'name', name);
  }

  // Now proceed with business logic
  // ...
}
```

### Pattern 2: Try-Catch for External Calls

**Wrap external calls, add context:**

```typescript
async function fetchUserFromAPI(userId: string): Promise<User> {
  try {
    const response = await fetch(`/api/users/${userId}`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new NotFoundError('User', userId);
      }
      throw new ExternalServiceError(
        'UserAPI',
        `HTTP ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    // Add context to any caught error
    if (error instanceof NotFoundError || error instanceof ExternalServiceError) {
      throw error; // Re-throw our custom errors
    }

    // Wrap unexpected errors
    throw new ExternalServiceError(
      'UserAPI',
      'Failed to fetch user',
      error as Error
    );
  }
}
```

### Pattern 3: Result Objects (for non-exceptional failures)

**When failure is part of normal flow:**

```typescript
type Result<T, E = Error> =
  | { success: true; value: T }
  | { success: false; error: E };

function parseJSON<T>(jsonString: string): Result<T> {
  try {
    const value = JSON.parse(jsonString);
    return { success: true, value };
  } catch (error) {
    return {
      success: false,
      error: new Error(`Invalid JSON: ${error.message}`)
    };
  }
}

// Usage
const result = parseJSON(input);
if (result.success) {
  console.log(result.value);
} else {
  console.error(result.error);
}
```

### Pattern 4: Global Error Handler (Express/APIs)

**Centralized error handling:**

```typescript
// Global error handler middleware
function errorHandler(
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
) {
  // Log error with context
  logger.error('Request error', {
    error: error.message,
    stack: error.stack,
    path: req.path,
    method: req.method,
    userId: req.user?.id
  });

  // Map custom errors to HTTP responses
  if (error instanceof ValidationError) {
    return res.status(400).json({
      error: 'Validation failed',
      field: error.field,
      message: error.message
    });
  }

  if (error instanceof NotFoundError) {
    return res.status(404).json({
      error: 'Resource not found',
      message: error.message
    });
  }

  if (error instanceof AuthenticationError) {
    return res.status(401).json({
      error: 'Authentication required',
      message: error.message
    });
  }

  if (error instanceof AuthorizationError) {
    return res.status(403).json({
      error: 'Forbidden',
      message: error.message
    });
  }

  // Default to 500 for unexpected errors
  // Don't expose internal details to users
  res.status(500).json({
    error: 'Internal server error',
    message: 'An unexpected error occurred'
    // Include error ID for correlation with logs
    errorId: generateErrorId()
  });
}
```

---

## Logging Strategy

### What to Log

#### Always Log
- ✅ Errors with full stack traces
- ✅ Request context (path, method, user)
- ✅ External service calls (success/failure)
- ✅ Authentication/authorization failures
- ✅ Business rule violations

#### Never Log
- ❌ Passwords or secrets
- ❌ Sensitive user data (SSN, credit cards, etc.)
- ❌ Complete request/response bodies (may contain secrets)

### Log Levels

- **ERROR**: Unexpected errors, failures that need attention
- **WARN**: Recoverable errors, deprecated usage, suspicious activity
- **INFO**: Important business events (user created, order placed)
- **DEBUG**: Detailed diagnostic information (dev/staging only)

### Log Format

```typescript
logger.error('Error message', {
  // Context
  userId: 'user-123',
  action: 'createOrder',

  // Error details
  error: {
    name: error.name,
    message: error.message,
    stack: error.stack
  },

  // Additional context
  orderId: 'order-456',
  timestamp: new Date().toISOString()
});
```

---

## Retry Strategy

### When to Retry
- ✅ Network timeouts
- ✅ Temporary service unavailability (503)
- ✅ Rate limiting (429) - with backoff
- ✅ Transient database deadlocks

### When NOT to Retry
- ❌ Validation errors (400)
- ❌ Authentication errors (401)
- ❌ Authorization errors (403)
- ❌ Not found (404)
- ❌ Business logic errors (422)

### Retry Pattern

```typescript
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;

      // Don't retry on non-retryable errors
      if (error instanceof ValidationError ||
          error instanceof NotFoundError ||
          error instanceof AuthenticationError) {
        throw error;
      }

      // Last attempt failed, throw
      if (attempt === maxRetries) {
        throw error;
      }

      // Exponential backoff: 1s, 2s, 4s
      const delay = baseDelay * Math.pow(2, attempt);
      await sleep(delay);
    }
  }

  throw lastError!;
}
```

---

## Error Messages

### User-Facing Messages
- **Clear and actionable**: "Email format is invalid. Please use format: user@domain.com"
- **No technical jargon**: Avoid "NullPointerException", "500 error"
- **Suggest solutions**: "File too large (5MB max). Try compressing it."
- **Polite tone**: "We couldn't process your request" not "Request failed"

### Developer-Facing Messages (Logs)
- **Technical details**: Include error codes, stack traces, IDs
- **Context**: What operation failed, with what data
- **Breadcrumbs**: Path leading to the error
- **Correlation IDs**: Link related log entries

---

## Testing Error Handling

### Always Test
- ✅ Invalid inputs trigger correct errors
- ✅ Error messages are helpful
- ✅ Errors are logged correctly
- ✅ HTTP status codes are correct
- ✅ Sensitive data is not leaked
- ✅ Retry logic works as expected

### Example Test

```typescript
describe('User creation error handling', () => {
  it('should throw ValidationError for invalid email', () => {
    expect(() => createUser('invalid-email', 'John'))
      .toThrow(ValidationError);
  });

  it('should return 400 for validation errors', async () => {
    const response = await request(app)
      .post('/users')
      .send({ email: 'invalid', name: 'John' });

    expect(response.status).toBe(400);
    expect(response.body.error).toBe('Validation failed');
    expect(response.body.field).toBe('email');
  });

  it('should not leak sensitive data in error response', async () => {
    // Simulate database error with connection string
    mockDB.create.mockRejectedValue(
      new Error('Connection failed: postgresql://user:password@host')
    );

    const response = await request(app)
      .post('/users')
      .send({ email: 'test@example.com', name: 'John' });

    expect(response.status).toBe(500);
    expect(response.body.message).not.toContain('password');
    expect(response.body.message).not.toContain('postgresql');
  });
});
```

---

## Monitoring & Alerting

### Metrics to Track
- Error rate by endpoint
- Error rate by error type
- Response time percentiles
- External service health

### Alert Thresholds
- **Critical**: Error rate > 5% for 5 minutes
- **Warning**: Error rate > 1% for 10 minutes
- **Info**: New error type detected

---

## Common Anti-Patterns to Avoid

### ❌ Silent Failures
```typescript
// BAD: Swallowing errors
try {
  await updateUser(userId, data);
} catch (error) {
  // Do nothing - error lost!
}

// GOOD: At minimum, log
try {
  await updateUser(userId, data);
} catch (error) {
  logger.error('Failed to update user', { userId, error });
  throw error; // Or handle appropriately
}
```

### ❌ Generic Error Messages
```typescript
// BAD
throw new Error('Invalid input');

// GOOD
throw new ValidationError(
  'Email must be in format: user@domain.com',
  'email',
  providedEmail
);
```

### ❌ Catching Too Broadly
```typescript
// BAD: Catches everything, including bugs
try {
  const user = await getUser(id);
  const result = user.calculate(); // Bug: user might be null
} catch (error) {
  return { error: 'User not found' }; // Misleading!
}

// GOOD: Catch specific errors
try {
  const user = await getUser(id);
  if (!user) throw new NotFoundError('User', id);
  const result = user.calculate(); // Bug would surface here
} catch (error) {
  if (error instanceof NotFoundError) {
    return { error: 'User not found' };
  }
  throw error; // Re-throw unexpected errors
}
```

### ❌ Using Errors for Control Flow
```typescript
// BAD: Using exceptions for non-exceptional cases
function findUser(id: string): User {
  const user = db.findById(id);
  if (!user) throw new Error('Not found'); // Normal case!
  return user;
}

// GOOD: Use null/undefined for expected "not found"
function findUser(id: string): User | null {
  return db.findById(id) ?? null;
}

// Or Result pattern for explicit handling
function findUser(id: string): Result<User> {
  const user = db.findById(id);
  return user
    ? { success: true, value: user }
    : { success: false, error: new NotFoundError('User', id) };
}
```

---

## Project-Specific Implementations

These are general preferences. Document **project-specific** error handling in:

`.ai/knowledge/patterns/error-handling.md`

Include:
- Specific error classes for this project
- Error handling middleware configuration
- Logging setup and format
- Monitoring/alerting configuration
- Examples from this codebase

---

Updated: 2025-11-08
