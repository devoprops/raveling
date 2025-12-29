import { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import apiClient from '../../utils/api';
import './UserManagement.css';

interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'designer' | 'player' | 'viewer';
  is_active: boolean;
  created_at?: string;
}

export default function UserManagement() {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchUsers();
    }
  }, [user]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/users/');
      setUsers(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async (userId: number, updates: Partial<User>) => {
    try {
      await apiClient.put(`/api/users/${userId}`, updates);
      await fetchUsers();
      setEditingUser(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update user');
    }
  };

  const handleCreateUser = async (userData: {
    username: string;
    email: string;
    password: string;
    role: User['role'];
    is_active: boolean;
  }) => {
    try {
      await apiClient.post('/api/users/', userData);
      await fetchUsers();
      setShowCreateForm(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create user');
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!confirm('Are you sure you want to delete this user?')) {
      return;
    }
    try {
      await apiClient.delete(`/api/users/${userId}`);
      await fetchUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete user');
    }
  };

  if (user?.role !== 'admin') {
    return (
      <div className="user-management">
        <div className="error-message">Access denied. Admin privileges required.</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="user-management">
        <div className="loading">Loading users...</div>
      </div>
    );
  }

  return (
    <div className="user-management">
      <div className="user-management-header">
        <h1>User Management</h1>
        <button onClick={() => setShowCreateForm(true)} className="create-button">
          + Create User
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showCreateForm && (
        <CreateUserForm
          onSubmit={handleCreateUser}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      <div className="users-table">
        <table>
          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.username}</td>
                <td>{u.email}</td>
                <td>
                  {editingUser?.id === u.id ? (
                    <select
                      value={editingUser.role}
                      onChange={(e) =>
                        setEditingUser({
                          ...editingUser,
                          role: e.target.value as User['role'],
                        })
                      }
                    >
                      <option value="admin">Admin</option>
                      <option value="designer">Designer</option>
                      <option value="player">Player</option>
                      <option value="viewer">Viewer</option>
                    </select>
                  ) : (
                    <span className={`role-badge role-${u.role}`}>{u.role}</span>
                  )}
                </td>
                <td>
                  {editingUser?.id === u.id ? (
                    <select
                      value={editingUser.is_active ? 'active' : 'inactive'}
                      onChange={(e) =>
                        setEditingUser({
                          ...editingUser,
                          is_active: e.target.value === 'active',
                        })
                      }
                    >
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  ) : (
                    <span className={`status-badge ${u.is_active ? 'active' : 'inactive'}`}>
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  )}
                </td>
                <td>
                  {u.created_at
                    ? new Date(u.created_at).toLocaleDateString()
                    : 'N/A'}
                </td>
                <td>
                  {editingUser?.id === u.id ? (
                    <div className="action-buttons">
                      <button
                        onClick={() =>
                          handleUpdateUser(u.id, {
                            role: editingUser.role,
                            is_active: editingUser.is_active,
                          })
                        }
                        className="save-button"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingUser(null)}
                        className="cancel-button"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <div className="action-buttons">
                      <button
                        onClick={() => setEditingUser(u)}
                        className="edit-button"
                      >
                        Edit
                      </button>
                      {u.id !== user?.id && (
                        <button
                          onClick={() => handleDeleteUser(u.id)}
                          className="delete-button"
                        >
                          Delete
                        </button>
                      )}
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function CreateUserForm({
  onSubmit,
  onCancel,
}: {
  onSubmit: (data: {
    username: string;
    email: string;
    password: string;
    role: User['role'];
    is_active: boolean;
  }) => void;
  onCancel: () => void;
}) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<User['role']>('player');
  const [isActive, setIsActive] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ username, email, password, role, is_active: isActive });
  };

  return (
    <div className="create-user-form">
      <h2>Create New User</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />
        </div>
        <div className="form-group">
          <label>Role</label>
          <select value={role} onChange={(e) => setRole(e.target.value as User['role'])}>
            <option value="admin">Admin</option>
            <option value="designer">Designer</option>
            <option value="player">Player</option>
            <option value="viewer">Viewer</option>
          </select>
        </div>
        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
            />
            Active
          </label>
        </div>
        <div className="form-actions">
          <button type="submit" className="save-button">Create</button>
          <button type="button" onClick={onCancel} className="cancel-button">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

