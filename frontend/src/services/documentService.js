import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const documentService = {
  uploadDocument: async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_URL}/documents/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const progress = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onUploadProgress(progress);
      },
    });

    return response.data;
  },

  getDocuments: async () => {
    const response = await axios.get(`${API_URL}/documents`);
    return response.data;
  }
};