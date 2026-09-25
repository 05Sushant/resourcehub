/**
 * Removes authentication tokens from localStorage, effectively logging the user out.
 */
export function logout(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}
