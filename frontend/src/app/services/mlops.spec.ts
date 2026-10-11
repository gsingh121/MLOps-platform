import { TestBed } from '@angular/core/testing';
import { Mlops } from './mlops';

describe('Mlops', () => {
  let service: Mlops;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Mlops);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
