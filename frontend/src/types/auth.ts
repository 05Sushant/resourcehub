export interface LoginResponse {
  access: string;
  refresh: string;
}

export interface RegisterResponse {
  id: number;
  username: string;
  email: string;
}

export interface ApiError {
  detail?: string;
  [key: string]: string | string[] | undefined;
}
