import api from './api';
import type { Resource } from '../types/resource';

export async function getResources(): Promise<Resource[]> {
  const response = await api.get<Resource[]>('/api/resources/');
  return response.data;
}
