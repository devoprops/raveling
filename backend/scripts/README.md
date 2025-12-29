# Admin Setup Scripts

## Creating Your First Admin User

Since there's no admin user initially, you need to create one using the command-line script.

### Local Development

1. Make sure your database is initialized:
   ```bash
   cd backend
   python -m src.database.init_db
   ```

2. Create your admin user:
   ```bash
   python scripts/create_admin.py --username YOUR_USERNAME --email YOUR_EMAIL --password YOUR_PASSWORD --init-db
   ```

   Or if the database is already initialized:
   ```bash
   python scripts/create_admin.py --username YOUR_USERNAME --email YOUR_EMAIL --password YOUR_PASSWORD
   ```

### Production (Railway)

1. SSH into your Railway service or use Railway CLI:
   ```bash
   railway run python scripts/create_admin.py --username YOUR_USERNAME --email YOUR_EMAIL --password YOUR_PASSWORD
   ```

### Example

```bash
python scripts/create_admin.py --username admin --email admin@example.com --password SecurePassword123!
```

**Important:** Choose a strong password and keep it secure!

## After Creating Admin

Once you have an admin account:

1. Log in through the web interface at `https://raveling.devocosm.com`
2. You'll see an "Admin" link in the header
3. Click it to access the User Management page where you can:
   - View all users
   - Create new users with any role
   - Update user roles (e.g., promote someone to Designer)
   - Activate/deactivate users
   - Delete users (except yourself)

## User Roles

- **Admin**: Full access, can manage users and approve configs
- **Designer**: Can create and edit design configs
- **Player**: Can view approved configs (for gameplay)
- **Viewer**: Read-only access to view configs

## Registration

Regular users can self-register through the web interface, but they can only choose:
- **Player** role
- **Viewer** role

To grant **Designer** or **Admin** roles, an existing admin must update the user's role through the User Management page.

