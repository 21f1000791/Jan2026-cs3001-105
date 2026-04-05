import { apiClient } from "./apiClient";

export const translationService = {
  async translateUI(texts, language) {
    const response = await apiClient.post("/translations/ui", {
      language,
      texts,
    });
    return response.data?.translations || {};
  },
};
