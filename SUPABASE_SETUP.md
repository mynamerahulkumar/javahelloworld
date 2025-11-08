# Supabase Setup Guide

## Overview

This application uses Supabase for authentication. Users are authenticated via Supabase and validated against a CSV whitelist for authorization.

## Prerequisites

1. A Supabase account (sign up at https://supabase.com)
2. A Supabase project created
3. Environment variables configured

## Step 1: Create Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Fill in project details:
   - **Name**: SRP Algo Trading (or your preferred name)
   - **Database Password**: Choose a strong password
   - **Region**: Choose closest to your users
4. Click "Create new project"
5. Wait for project to be provisioned (takes a few minutes)

## Step 2: Get Supabase Credentials

1. In your Supabase project dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon/public key** (starts with `eyJ...`)
   - **service_role key** (starts with `eyJ...`) - **Keep this secret!**

## Step 3: Configure Backend Environment Variables

Add to `backend/.env`:

```env
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ... (your service_role key)
SUPABASE_ANON_KEY=eyJ... (optional, your anon key)
```

## Step 4: Configure Frontend Environment Variables

Add to `frontend/.env.local`:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ... (your anon/public key)
```

## Step 5: Migrate Users to Supabase

### Option A: Migrate from CSV

Run the migration script to create Supabase users from your CSV file:

```bash
cd backend
python scripts/migrate_users_to_supabase.py
```

This will:
- Read users from `backend/privatedata/srp_client_trading.csv`
- Create Supabase users with their emails and passwords
- Store `client_id` in user metadata

### Option B: Migrate from Auth0 (if applicable)

If you have Auth0 users to migrate:

1. Export users from Auth0 (JSON format)
2. Run migration script:

```bash
cd backend
python scripts/migrate_users_to_supabase.py --auth0 --auth0-file path/to/auth0_users.json
```

**Note**: Auth0 passwords cannot be migrated. Users will need to reset their passwords.

### Dry Run

To see what would be migrated without actually creating users:

```bash
python scripts/migrate_users_to_supabase.py --dry-run
```

## Step 6: Configure Supabase Authentication

1. In Supabase dashboard, go to **Authentication** → **Settings**
2. Configure email authentication:
   - Enable "Enable email signup"
   - Configure email templates (optional)
   - Set up email confirmation (optional, recommended for production)

3. Configure email provider:
   - Use Supabase's built-in email service (for development)
   - Or configure SMTP for production

## Step 7: User Whitelist

Users must be in the CSV whitelist (`backend/privatedata/srp_client_trading.csv`) to access the application, even if they have a Supabase account.

The CSV file should have the format:
```csv
srp_client_emailid,srp_client_id,srp_client_password
user@example.com,123456,password123
```

## Step 8: Test Authentication

1. Start the backend:
   ```bash
   cd backend
   ./start.sh
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Navigate to http://localhost:3000/login
4. Try logging in with a user from your CSV file

## Troubleshooting

### Error: "Supabase authentication is not configured"
- Check that `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set in `backend/.env`
- Restart the backend server after adding environment variables

### Error: "User is not authorized"
- User must exist in `backend/privatedata/srp_client_trading.csv`
- Email in CSV must match Supabase user email (case-insensitive)

### Error: "Invalid or expired token"
- User session may have expired
- Try logging out and logging back in
- Check Supabase dashboard for authentication logs

### Users cannot login
- Verify user exists in Supabase (check Authentication → Users in dashboard)
- Verify user email matches CSV file
- Check Supabase logs for authentication errors

## Production Considerations

1. **Email Confirmation**: Enable email confirmation in Supabase settings
2. **Password Reset**: Configure password reset flow in Supabase
3. **Rate Limiting**: Configure rate limiting in Supabase
4. **Security**: 
   - Never expose `SUPABASE_SERVICE_ROLE_KEY` in frontend code
   - Use environment variables for all secrets
   - Enable RLS (Row Level Security) if using Supabase database features

## Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Auth Guide](https://supabase.com/docs/guides/auth)
- [Next.js + Supabase Guide](https://supabase.com/docs/guides/getting-started/quickstarts/nextjs)






