export interface Job {
  id: number;
  resource: number;
  operation: string;
  parameters: Record<string, unknown>;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  input_file: string;
  result_file: string;
  celery_task_id: string;
  error_message: string;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface ProfileResult {
  rows: number;
  columns: number;
  columns_info: {
    name: string;
    type: string;
    empty_count: number;
  }[];
}
