import { useState, useRef } from 'react';
import apiClient from '../../utils/api';
import './ThumbnailPicker.css';

interface ThumbnailPickerProps {
  thumbnailPath?: string;
  itemName: string;
  onThumbnailChange: (path: string) => void;
}

export default function ThumbnailPicker({ thumbnailPath, itemName, onThumbnailChange }: ThumbnailPickerProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [preview, setPreview] = useState<string | null>(thumbnailPath || null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setError('Invalid file type. Please select a PNG, JPG, GIF, or WebP image.');
      return;
    }

    // Validate file size (2MB max)
    if (file.size > 2 * 1024 * 1024) {
      setError('File size exceeds 2MB limit.');
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Upload to backend
    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post(
        `/api/weapons/upload-thumbnail?item_name=${encodeURIComponent(itemName)}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      onThumbnailChange(response.data.thumbnail_path);
      setError('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload thumbnail');
      setPreview(null);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleRemove = () => {
    setPreview(null);
    onThumbnailChange('');
    setError('');
  };

  return (
    <div className="thumbnail-picker">
      <label className="thumbnail-picker-label">Thumbnail Image</label>
      <div className="thumbnail-picker-content">
        {preview ? (
          <div className="thumbnail-preview-container">
            <img src={preview} alt="Thumbnail preview" className="thumbnail-preview" />
            <button
              type="button"
              className="thumbnail-remove-btn"
              onClick={handleRemove}
              disabled={uploading}
            >
              Remove
            </button>
          </div>
        ) : (
          <div className="thumbnail-upload-area">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
              onChange={handleFileSelect}
              disabled={uploading}
              className="thumbnail-file-input"
              id="thumbnail-upload"
            />
            <label htmlFor="thumbnail-upload" className="thumbnail-upload-label">
              {uploading ? 'Uploading...' : 'Choose Image (200x200px recommended)'}
            </label>
          </div>
        )}
        {error && <div className="thumbnail-error">{error}</div>}
      </div>
    </div>
  );
}

