/**
 * App Configuration
 * Environment-specific settings
 */

// Get API base URL from environment or use default
// For development with Expo, use your computer's IP address
// For production, use your deployed backend URL
export const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

// Export configuration object
export default {
  apiBaseUrl: API_BASE_URL,
};
