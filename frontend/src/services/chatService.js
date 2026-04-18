// src/services/chatService.js
import { apiClient } from './apiClient';

export const chatService = {
  async sendMessage(message) {
    try {
      // Change this line:
      const response = await apiClient.post('/chat', { message }); 
      return response.data.reply;
    } catch (error) {
      console.error("Chat API Error:", error);
      throw new Error("Failed to connect to the AI Assistant.");
    }
  }
};