// Create sveltekit server function to return data to page on load

import { PUBLIC_API_BASE_URL } from '$env/static/public';

export async function load({ fetch }) {
  const apiUrl = PUBLIC_API_BASE_URL || 'http://localhost:5000';
  const res = await fetch(`${apiUrl}/airports`);
  const airports = await res.json();
  return { airports };
}

export const actions = {
  getDelay: async ({ fetch, request }) => {
    try {
      const apiUrl = PUBLIC_API_BASE_URL || 'http://localhost:5000';
      const data = await request.formData();

      const day_of_week = data.get('day');
      const airport_id = data.get('airport');

      // Validate inputs before sending
      if (!day_of_week || !airport_id) {
        return { error: 'Missing required parameters' };
      }

      // Use URLSearchParams for safe parameter encoding
      const params = new URLSearchParams();
      params.append('day_of_week', String(day_of_week));
      params.append('airport_id', String(airport_id));

      const res = await fetch(`${apiUrl}/predict?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!res.ok) {
        const error = await res.json();
        return { error: error.error || 'Prediction failed' };
      }

      const result = await res.json();
      return { result };
    } catch (err) {
      console.error('Error fetching prediction:', err);
      return { error: 'Failed to fetch prediction' };
    }
  },
};