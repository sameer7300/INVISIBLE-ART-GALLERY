import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { 
  UserLogin, 
  UserRegistration, 
  UserAuthResponse,
  User, 
  Artwork, 
  ArtworkCreate,
  Comment,
  CommentCreate
} from '../types';

// Create an axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor for authorization
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth endpoints
const auth = {
  login: async (credentials: UserLogin): Promise<UserAuthResponse> => {
    const response = await apiClient.post<UserAuthResponse>('/auth/login/', credentials);
    return response.data;
  },

  register: async (data: UserRegistration): Promise<UserAuthResponse> => {
    const response = await apiClient.post<UserAuthResponse>('/auth/register/', data);
    return response.data;
  },

  logout: async (refreshToken: string): Promise<void> => {
    await apiClient.post('/auth/logout/', { refresh: refreshToken });
  },

  refreshToken: async (refreshToken: string): Promise<{ access: string }> => {
    const response = await apiClient.post<{ access: string }>('/auth/refresh/', { refresh: refreshToken });
    return response.data;
  },

  getProfile: async (): Promise<User> => {
    const response = await apiClient.get<User>('/users/me/');
    return response.data;
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await apiClient.patch<User>('/users/me/', data);
    return response.data;
  },

  changePassword: async (oldPassword: string, newPassword: string): Promise<void> => {
    await apiClient.post('/users/me/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
      new_password_confirm: newPassword,
    });
  },
};

// Artwork endpoints
const artworks = {
  getAll: async (page: number = 1, filters?: Record<string, any>): Promise<{ results: Artwork[], count: number }> => {
    const response = await apiClient.get<{ results: Artwork[], count: number }>(
      '/artworks/',
      { params: { page, ...filters } }
    );
    return response.data;
  },

  getById: async (id: string): Promise<Artwork> => {
    const response = await apiClient.get<Artwork>(`/artworks/${id}/`);
    return response.data;
  },

  create: async (artworkData: ArtworkCreate): Promise<Artwork> => {
    // Handle file uploads with FormData
    const formData = new FormData();
    
    // Add text fields
    formData.append('title', artworkData.title);
    if (artworkData.description) {
      formData.append('description', artworkData.description);
    }
    formData.append('content_type', artworkData.content_type);
    
    // Add artwork file
    formData.append('artwork_file', artworkData.artwork_file);
    
    // Add placeholder image if provided
    if (artworkData.placeholder_image) {
      formData.append('placeholder_image', artworkData.placeholder_image);
    }
    
    // Add reveal conditions as JSON
    formData.append('reveal_conditions', JSON.stringify(artworkData.reveal_conditions));
    
    const response = await apiClient.post<Artwork>('/artworks/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  update: async (id: string, data: Partial<Artwork>): Promise<Artwork> => {
    const response = await apiClient.patch<Artwork>(`/artworks/${id}/`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/artworks/${id}/`);
  },

  // Comments
  addComment: async (artworkId: string, comment: CommentCreate): Promise<Comment> => {
    const response = await apiClient.post<Comment>(`/artworks/${artworkId}/add_comment/`, comment);
    return response.data;
  },

  // Artist's own artworks
  getMyArtworks: async (): Promise<Artwork[]> => {
    const response = await apiClient.get<Artwork[]>('/artworks/my-artworks/');
    return response.data;
  },

  // Search
  search: async (query: string): Promise<Artwork[]> => {
    const response = await apiClient.get<Artwork[]>('/artworks/search/', {
      params: { query },
    });
    return response.data;
  },
};

// Export the API service
const apiService = {
  auth,
  artworks,
};

export default apiService; 