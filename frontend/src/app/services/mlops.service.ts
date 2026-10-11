import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface MLModel { id: string; name: string; description: string; tags: string[]; }
export interface Deployment { id: string; version_id: string; environment: string; state: string; created_at: string; }

@Injectable({ providedIn: 'root' })
export class MlopsService {
  private apiUrl = 'http://localhost:8000';
  constructor(private http: HttpClient) {}
  getModels(): Observable<MLModel[]> { return this.http.get<MLModel[]>(`${this.apiUrl}/models`); }
  getDeployments(): Observable<Deployment[]> { return this.http.get<Deployment[]>(`${this.apiUrl}/deployments`); }
  rollback(deploymentId: string): Observable<any> { return this.http.post(`${this.apiUrl}/deployments/${deploymentId}/rollback`, {}); }
}
