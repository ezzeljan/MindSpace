export const apiFetch = async (url, options = {}) => {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const response = await fetch(url, {
    ...options,
    headers,
  });
  if (response.status === 401) {
    clearAuthToken();
    window.location.reload();
  }
  return response.json();
};

export const getAuthToken = () => localStorage.getItem('authToken');

export const setAuthToken = (token) => localStorage.setItem('authToken', token);

export const clearAuthToken = () => localStorage.removeItem('authToken');