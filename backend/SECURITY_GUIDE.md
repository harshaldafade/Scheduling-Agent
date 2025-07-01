# Security Guide for AI Scheduling Agent

## Overview

This document outlines the comprehensive security measures implemented in the AI Scheduling Agent to protect against common vulnerabilities and ensure secure authentication.

## 🔒 Security Features Implemented

### 1. OAuth 2.0 Security Enhancements

#### State Parameter Validation
- **Implementation**: Each OAuth request includes a cryptographically secure state parameter
- **Storage**: State parameters are stored in Redis with expiration (10 minutes)
- **Validation**: State parameters are validated on callback to prevent CSRF attacks
- **Cleanup**: Used state parameters are immediately deleted

#### Secure OAuth Flow
```python
# Generate secure state
state = secrets.token_urlsafe(32)

# Store with expiration
redis_client.setex(f"oauth_state:{state}", 600, json.dumps({
    "provider": provider,
    "created_at": time.time(),
    "expires_at": time.time() + 600
}))
```

### 2. JWT Token Security

#### Enhanced Token Claims
- **Issuer (iss)**: Validates token was issued by our application
- **Audience (aud)**: Ensures token is intended for our users
- **JWT ID (jti)**: Unique identifier for each token
- **Not Before (nbf)**: Prevents token use before valid time
- **Issued At (iat)**: Token creation timestamp

#### Token Blacklisting
- **Implementation**: Invalidated tokens are stored in Redis
- **Expiration**: Blacklisted tokens expire with the original token
- **Hash Storage**: Token hashes are stored for security

#### Refresh Token Support
- **Long-lived refresh tokens**: 7 days validity
- **Automatic rotation**: New refresh tokens on each use
- **Secure storage**: Refresh tokens stored securely

### 3. Rate Limiting

#### Authentication Rate Limiting
- **OAuth attempts**: 10 attempts per 5 minutes per IP
- **General API**: 100 requests per 15 minutes per IP
- **Redis-based**: Scalable rate limiting with Redis

#### Implementation
```python
def _check_rate_limit(self, identifier: str, limit: int = 10, window: int = 300):
    key = f"rate_limit:{identifier}"
    current = redis_client.get(key)
    
    if current is None:
        redis_client.setex(key, window, 1)
        return True
    
    count = int(current)
    if count >= limit:
        return False
    
    redis_client.incr(key)
    return True
```

### 4. Security Headers

#### HTTP Security Headers
- **X-Content-Type-Options**: `nosniff` - Prevents MIME type sniffing
- **X-Frame-Options**: `DENY` - Prevents clickjacking
- **X-XSS-Protection**: `1; mode=block` - XSS protection
- **Referrer-Policy**: `strict-origin-when-cross-origin`
- **Strict-Transport-Security**: `max-age=31536000; includeSubDomains`
- **Content-Security-Policy**: Restricts resource loading

### 5. CORS Configuration

#### Restrictive CORS Settings
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Configured origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

### 6. Input Validation

#### OAuth Parameter Validation
- **Authorization Code**: Required and validated
- **State Parameter**: Validated against stored state
- **User Information**: Required fields validated
- **Email Validation**: Ensures valid email format

#### Request Validation
- **Pydantic Models**: All requests validated with Pydantic
- **Type Checking**: Strict type validation
- **Email Validation**: EmailStr for email validation

### 7. Error Handling

#### Secure Error Responses
- **No Information Leakage**: Generic error messages
- **Logging**: Detailed errors logged server-side
- **Rate Limit Errors**: Proper 429 responses
- **Authentication Errors**: Secure 401 responses

## 🚀 Production Deployment Security

### 1. Environment Variables

#### Required Security Variables
```bash
# Generate secure secret key
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# Security Settings
ENVIRONMENT=production
DEBUG=false
ENABLE_SECURITY_HEADERS=true
SESSION_COOKIE_SECURE=true
```

### 2. Database Security

#### PostgreSQL Configuration
```bash
# Use PostgreSQL in production
DATABASE_URL=postgresql://user:password@host:port/database

# Enable SSL
POSTGRES_SSL_MODE=require
```

#### Redis Security
```bash
# Secure Redis configuration
REDIS_URL=redis://:password@host:port/database
REDIS_SSL=true
```

### 3. Server Security

#### HTTPS Configuration
- **SSL/TLS**: Enable HTTPS in production
- **HSTS**: Strict Transport Security headers
- **Certificate**: Valid SSL certificate required

#### Firewall Configuration
```bash
# Allow only necessary ports
ufw allow 443/tcp  # HTTPS
ufw allow 80/tcp   # HTTP (redirect to HTTPS)
ufw deny 22/tcp    # SSH (use key-based auth)
```

### 4. OAuth Provider Configuration

#### Google OAuth Setup
1. Go to Google Cloud Console
2. Create OAuth 2.0 credentials
3. Add authorized redirect URIs
4. Configure scopes: `openid email profile`

#### GitHub OAuth Setup
1. Go to GitHub Developer Settings
2. Create OAuth App
3. Add callback URL
4. Configure scopes: `user:email`

### 5. Monitoring and Logging

#### Security Logging
```python
# Log security events
logger.warning(f"Failed login attempt for user: {email}")
logger.error(f"OAuth state validation failed: {state}")
logger.info(f"User logged in: {user_id}")
```

#### Rate Limit Monitoring
- Monitor rate limit violations
- Alert on suspicious activity
- Track authentication patterns

## 🔍 Security Testing

### 1. OAuth Security Tests
```python
def test_oauth_state_validation():
    # Test state parameter validation
    # Test expired state parameters
    # Test invalid state parameters

def test_oauth_rate_limiting():
    # Test rate limiting on OAuth endpoints
    # Test rate limit bypass attempts
```

### 2. JWT Security Tests
```python
def test_jwt_token_validation():
    # Test token signature validation
    # Test token expiration
    # Test token blacklisting
    # Test refresh token rotation
```

### 3. API Security Tests
```python
def test_rate_limiting():
    # Test general API rate limiting
    # Test authentication endpoint rate limiting

def test_security_headers():
    # Test presence of security headers
    # Test CORS configuration
```

## 🛡️ Security Checklist

### Pre-Deployment
- [ ] Generate secure SECRET_KEY
- [ ] Configure OAuth providers
- [ ] Set up HTTPS certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Test all security features

### Post-Deployment
- [ ] Monitor authentication logs
- [ ] Check rate limit violations
- [ ] Verify security headers
- [ ] Test OAuth flows
- [ ] Monitor error rates
- [ ] Regular security audits

## 🚨 Incident Response

### Security Breach Response
1. **Immediate Actions**
   - Revoke all active tokens
   - Block suspicious IPs
   - Increase rate limiting
   - Monitor for unusual activity

2. **Investigation**
   - Review authentication logs
   - Check for data breaches
   - Analyze attack vectors
   - Document incident

3. **Recovery**
   - Reset affected user accounts
   - Update security measures
   - Notify affected users
   - Implement additional protections

## 📚 Additional Resources

- [OAuth 2.0 Security Best Practices](https://tools.ietf.org/html/rfc6819)
- [JWT Security Guidelines](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)

## 🔧 Security Configuration Examples

### Nginx Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Docker Security
```dockerfile
# Use non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Copy only necessary files
COPY --chown=appuser:appuser app/ /app/app/
COPY --chown=appuser:appuser requirements.txt /app/

# Set proper permissions
RUN chmod -R 755 /app
```

This security guide ensures that the AI Scheduling Agent is deployed with enterprise-grade security measures and follows industry best practices for authentication and authorization. 