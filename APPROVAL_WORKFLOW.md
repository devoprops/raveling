# Approval Workflow Documentation

## Architecture Overview

The system uses a two-tier storage model:

1. **Design Repository (GitHub)**: All configs, drafts, WIP, and approved configs
2. **Production Database**: Only approved configs ready for game use

## Workflow

### 1. Design Phase
- Designers create/edit configs in GitHub via API
- Configs are stored in `src/configs/{type}s/{name}.yaml`
- Database stores metadata (name, type, owner, GitHub path, approval status)

**Endpoints:**
- `GET /api/{items|skills|characters}/` - List design configs
- `GET /api/{items|skills|characters}/{id}` - Get design config
- `POST /api/{items|skills|characters}/` - Create design config (Designer/Admin)
- `PUT /api/{items|skills|characters}/{id}` - Update design config (Designer/Admin)
- `DELETE /api/{items|skills|characters}/{id}` - Delete design config (Designer/Admin)

### 2. Approval Phase
- Admin or Designer approves a config
- Config content is copied from GitHub to production database
- Design config's `is_approved` flag is set to `true`

**Endpoints:**
- `POST /api/approval/{items|skills|characters}/{config_id}/approve` - Approve config (Designer/Admin)

### 3. Production Use
- Game runtime uses approved configs from database
- Fast access, no GitHub API calls needed
- Configs can be used to initialize game objects

**Endpoints:**
- `GET /api/approval/{items|skills|characters}/approved` - List all approved configs
- `GET /api/approval/{items|skills|characters}/approved/{name}` - Get approved config by name

### 4. Re-approval
- Edit config in GitHub (via design endpoints)
- Re-approve to update production database
- Existing approved config is updated, not duplicated

## Database Models

### Config (Design Configs)
- Stores metadata for GitHub-stored configs
- Tracks approval status
- Links to owner and approver

### ApprovedConfig (Production Configs)
- Stores full config content (JSON string)
- Fast access for game runtime
- Links back to source design config
- Unique by name (re-approval updates existing)

## Example Flow

1. **Designer creates item:**
   ```bash
   POST /api/items/
   {
     "name": "rusty_sword_of_fire",
     "content": {...},
     "description": "A rusty sword imbued with fire"
   }
   ```
   - Saved to GitHub: `src/configs/items/rusty_sword_of_fire.yaml`
   - Metadata saved to `configs` table
   - `is_approved = false`

2. **Designer approves item:**
   ```bash
   POST /api/approval/items/1/approve
   ```
   - Content loaded from GitHub
   - Saved to `approved_configs` table
   - Design config's `is_approved = true`

3. **Game uses approved config:**
   ```bash
   GET /api/approval/items/approved/rusty_sword_of_fire
   ```
   - Returns config from database (fast)
   - Use to initialize game object

4. **Designer updates and re-approves:**
   ```bash
   PUT /api/items/1
   {
     "content": {...updated...}
   }
   POST /api/approval/items/1/approve
   ```
   - Updated in GitHub
   - Re-approval updates existing approved config in database

## Permissions

- **Create/Edit Design Configs**: Designer, Admin
- **Approve Configs**: Designer, Admin
- **View Design Configs**: All authenticated users (their own)
- **View Approved Configs**: All authenticated users

## Benefits

1. **Version Control**: All configs in GitHub with full history
2. **Fast Production Access**: Approved configs in database
3. **Separation of Concerns**: Design vs. production
4. **Re-approval**: Easy updates without losing history
5. **Audit Trail**: Track who approved what and when

