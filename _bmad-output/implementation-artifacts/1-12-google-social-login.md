# Story 1.12: Google Social Login

Status: ready-for-dev

## Story

As a new or returning user,
I want to log in or register using my Google account,
so that I can access the application quickly without creating a separate password.

## Acceptance Criteria

1. **AC1: Google Login Button** - The login page displays a "Continue with Google" button that redirects to Google OAuth.
2. **AC2: Google Signup Button** - The signup page displays a "Sign up with Google" button that redirects to Google OAuth.
3. **AC3: New User Registration** - When a user authenticates with Google for the first time, a new account is automatically created using their Google email.
4. **AC4: Existing User Login** - When a user authenticates with Google and an account with that email already exists, they are logged into that existing account.
5. **AC5: Session Creation** - Upon successful Google authentication, a Django session is created.
6. **AC6: Error Handling** - If Google authentication fails or is cancelled, user is redirected back with appropriate error state.
7. **AC7: Dashboard Redirect** - After successful authentication, the user is redirected to frontend `/dashboard`.
8. **AC8: Conditional Button Display** - Google login/signup buttons are only displayed if backend has Google OAuth configured (client ID/secret present).

## Tasks / Subtasks

- [ ] Task 1: Backend - Install and configure django-allauth (AC: 3, 4, 5)
  - [ ] 1.1: Add `django-allauth` to dependencies
  - [ ] 1.2: Add allauth apps to INSTALLED_APPS
  - [ ] 1.3: Configure SOCIALACCOUNT_PROVIDERS for Google
  - [ ] 1.4: Add allauth URLs to urlpatterns
  - [ ] 1.5: Run migrations for allauth tables
  - [ ] 1.6: Configure redirect URLs for SPA (LOGIN_REDIRECT_URL, etc.)

- [ ] Task 2: Backend - Auth providers endpoint (AC: 8)
  - [ ] 2.1: Create `GET /api/public/auth/providers` endpoint
  - [ ] 2.2: Return list of configured OAuth providers (check SocialApp exists with credentials)
  - [ ] 2.3: Update OpenAPI schema

- [ ] Task 3: Backend - Google provider setup (AC: 1-5)
  - [ ] 3.1: Create SocialApp entry via Django admin or data migration
  - [ ] 3.2: Configure Google Client ID and Secret from environment variables

- [ ] Task 4: Frontend - Google OAuth buttons (AC: 1, 2, 6, 7, 8)
  - [ ] 4.1: Fetch available providers from `/api/public/auth/providers`
  - [ ] 4.2: Conditionally render Google button only if 'google' in providers
  - [ ] 4.3: Add Google login button to `login-form.tsx`
  - [ ] 4.4: Add Google signup button to `signup-form.tsx`
  - [ ] 4.5: Handle redirect back from OAuth (success/error states)

- [ ] Task 5: Configuration & Documentation (AC: 1-7)
  - [ ] 5.1: Document Google Cloud Console setup
  - [ ] 5.2: Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET env vars
  - [ ] 5.3: Update `.env.example` files

## Dev Notes

### Technical Decision: django-allauth with Redirect Flow

**Why django-allauth:**
- Battle-tested library for Django social authentication
- Handles all OAuth complexity (token exchange, user creation, account linking)
- Actively maintained (latest release Nov 2025)
- Source: [django-allauth docs](https://docs.allauth.org/en/latest/)

**Why Redirect Flow (not headless/API):**
- Simpler implementation - frontend just links to backend URL
- django-allauth handles entire OAuth dance
- No frontend OAuth library needed

### OAuth Flow (Backend Redirect)

```
Frontend: Fetch /api/public/auth/providers → ["google"]
         ↓
User clicks "Continue with Google" (only shown if google in providers)
         ↓
Frontend: window.location = "/accounts/google/login/?next={frontend_url}"
         ↓
Backend (allauth): Redirects to Google OAuth
         ↓
User authenticates with Google
         ↓
Google redirects to: /accounts/google/login/callback/
         ↓
Backend (allauth): Verifies token, creates/finds user, creates session
         ↓
Backend: Redirects to frontend (LOGIN_REDIRECT_URL or ?next param)
         ↓
Frontend: Detects session, updates auth context
```

### New Endpoint: Auth Providers

**Purpose:** Allow frontend to know which OAuth providers are configured

```python
# public_api/auth.py

class AuthProvidersResponse(Schema):
    providers: list[str]  # e.g., ["google"]

@auth_router.get("/providers", response=AuthProvidersResponse, auth=None)
def get_auth_providers(request: HttpRequest):
    """Return list of configured OAuth providers."""
    from allauth.socialaccount.models import SocialApp

    providers = []

    # Check if Google is configured with credentials
    if SocialApp.objects.filter(
        provider='google',
        client_id__isnull=False,
    ).exclude(client_id='').exists():
        providers.append('google')

    return {"providers": providers}
```

### Architecture Compliance

**Integration with Existing Auth:**
- django-allauth creates Django sessions (same as current email/password)
- Uses same `CustomUser` model
- Works alongside existing Django Ninja auth endpoints
- No changes needed to existing login/logout flow

**Files to Modify:**

Backend:
- `pyproject.toml` - Add django-allauth dependency
- `shargain/settings/base.py` - Add allauth configuration
- `shargain/urls.py` - Add allauth URLs
- `shargain/public_api/auth.py` - Add providers endpoint
- `shargain/public_api/schemas.py` - Add response schema
- Run migrations

Frontend:
- `frontend/src/components/auth/login-form.tsx` - Add conditional Google button
- `frontend/src/components/auth/signup-form.tsx` - Add conditional Google button
- `frontend/src/hooks/useAuthProviders.ts` - New hook to fetch providers
- `frontend/src/routes/auth/signin.tsx` - Handle redirect callback

### Backend Configuration

```python
# settings/base.py

INSTALLED_APPS = [
    ...
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    ...
    'allauth.account.middleware.AccountMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'  # or 'optional' for MVP

# Social account settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Redirect after social login (to frontend)
LOGIN_REDIRECT_URL = env('FRONTEND_URL', default='http://localhost:5173') + '/dashboard'
ACCOUNT_LOGOUT_REDIRECT_URL = env('FRONTEND_URL', default='http://localhost:5173') + '/auth'

# Auto-connect social accounts to existing users with same email
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
```

```python
# urls.py
urlpatterns = [
    ...
    path('accounts/', include('allauth.urls')),
]
```

### Frontend Implementation

**Providers hook:**
```tsx
// hooks/useAuthProviders.ts
export function useAuthProviders() {
  return useQuery({
    queryKey: ['auth-providers'],
    queryFn: () => shargainPublicApiAuthProvidersView(),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });
}
```

**Conditional Google button:**
```tsx
// In login-form.tsx
const { data: providers } = useAuthProviders();
const isGoogleEnabled = providers?.providers.includes('google');

{isGoogleEnabled && (
  <a href={googleLoginUrl} className="...">
    <GoogleIcon />
    Continue with Google
  </a>
)}
```

### Environment Variables

```bash
# Backend (.env)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
FRONTEND_URL=http://localhost:5173

# Frontend (.env.development)
VITE_API_URL=http://localhost:8000
```

### Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project
3. APIs & Services → Credentials → Create OAuth client ID
4. Application type: Web application
5. Authorized JavaScript origins:
   - `http://localhost:8000` (dev backend)
   - `https://your-api-domain.com` (prod)
6. Authorized redirect URIs:
   - `http://localhost:8000/accounts/google/login/callback/` (dev)
   - `https://your-api-domain.com/accounts/google/login/callback/` (prod)
7. Copy Client ID and Secret to environment variables

### Django Admin / Data Migration Setup

Option A - Django Admin (manual):
1. Go to `/admin/socialaccount/socialapp/`
2. Add Social Application: Provider=Google, Client ID, Secret Key
3. Select your site

Option B - Data migration (automated):
```python
# accounts/migrations/000X_create_google_socialapp.py
def create_google_app(apps, schema_editor):
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    Site = apps.get_model('sites', 'Site')

    client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')

    if client_id and client_secret:
        app, _ = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id,
                'secret': client_secret,
            }
        )
        app.sites.add(Site.objects.get_current())
```

### Edge Cases

1. **No Google credentials configured**: `/providers` returns `[]`, buttons hidden
2. **Email already exists (password user)**: `SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT` links accounts
3. **OAuth cancelled**: User returns to frontend, no session created
4. **OAuth error**: allauth redirects with error - show message on frontend

### Testing Requirements

- Test: `/providers` returns `["google"]` when configured
- Test: `/providers` returns `[]` when not configured
- Test: Google button hidden when provider not available
- Test: Full OAuth flow (dev environment with real Google account)
- Test: New user created on first Google login
- Test: Existing user logged in when email matches

### Project Structure Notes

- Alignment: Uses Django's auth system (sessions) - matches existing pattern
- New endpoint `/api/public/auth/providers` follows existing auth router pattern
- Frontend hook follows existing React Query patterns
- Detected variance: allauth uses its own URL namespace (`/accounts/`) separate from `/api/public/auth/`

### References

- [Source: shargain/public_api/auth.py] - Existing auth endpoints pattern
- [Source: shargain/settings/base.py] - Existing auth settings
- [Source: frontend/src/components/auth/login-form.tsx] - Login form to modify
- [django-allauth Google docs](https://docs.allauth.org/en/latest/socialaccount/providers/google.html)
- [django-allauth React SPA example](https://github.com/pennersr/django-allauth/blob/main/examples/react-spa/README.org)

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
