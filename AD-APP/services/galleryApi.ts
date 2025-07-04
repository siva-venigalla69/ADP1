import api from './api';

export interface Design {
  id: number;
  title: string;
  description?: string;
  image_url: string;
  category: string;
  tags?: string;
  created_at: string;
  updated_at: string;
}

export interface DesignsResponse {
  designs: Design[];
  totalCount: number;
}

class GalleryAPI {
  async getDesigns(page: number = 1, limit: number = 20): Promise<DesignsResponse> {
    const response = await api.get(`/api/designs?page=${page}&limit=${limit}`);
    return response.data;
  }

  async getDesignById(id: number): Promise<Design> {
    const response = await api.get(`/api/designs/${id}`);
    return response.data;
  }

  async searchDesigns(query: string, category?: string): Promise<DesignsResponse> {
    const params = new URLSearchParams({ q: query });
    if (category) {
      params.append('category', category);
    }
    const response = await api.get(`/api/designs/search?${params}`);
    return response.data;
  }

  // Admin functions
  async createDesign(designData: Omit<Design, 'id' | 'created_at' | 'updated_at'>): Promise<Design> {
    const response = await api.post('/api/admin/designs', designData);
    return response.data;
  }

  async updateDesign(id: number, designData: Partial<Design>): Promise<Design> {
    const response = await api.put(`/api/admin/designs/${id}`, designData);
    return response.data;
  }

  async deleteDesign(id: number): Promise<void> {
    await api.delete(`/api/admin/designs/${id}`);
  }

  async getUploadUrl(filename: string, contentType: string): Promise<{ uploadUrl: string; publicUrl: string }> {
    const response = await api.post('/api/upload-url', { filename, contentType });
    return response.data;
  }
}

export const galleryApi = new GalleryAPI(); 