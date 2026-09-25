import api from './api';
import type { Job } from '../types/job';

export async function getJobs(): Promise<Job[]> {
  const response = await api.get<Job[]>('/api/jobs/');
  return response.data;
}

export async function getJob(id: number): Promise<Job> {
  const response = await api.get<Job>(`/api/jobs/${id}/`);
  return response.data;
}

export async function createJob(formData: FormData): Promise<Job> {
  const response = await api.post<Job>('/api/jobs/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}
