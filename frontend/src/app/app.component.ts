import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { MlopsService, MLModel, Deployment } from './services/mlops.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, HttpClientModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  models: MLModel[] = [];
  deployments: Deployment[] = [];
  loading = true;
  error = '';

  constructor(private mlopsService: MlopsService) {}

  ngOnInit() { this.fetchData(); }

  fetchData() {
    this.mlopsService.getModels().subscribe({
      next: (data) => { this.models = data; this.loading = false; },
      error: (err) => { this.error = 'Failed to load data'; this.loading = false; }
    });
    this.mlopsService.getDeployments().subscribe(data => this.deployments = data);
  }

  rollback(id: string) {
    this.mlopsService.rollback(id).subscribe(() => this.fetchData());
  }
}
