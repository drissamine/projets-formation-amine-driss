import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { Navbar } from './navbar';
import { AuthService } from '../../services/auth.service';
import { of } from 'rxjs';

describe('Navbar', () => {
  let component: Navbar;
  let fixture: ComponentFixture<Navbar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Navbar, RouterTestingModule],
      providers: [
        {
          provide: AuthService,
          useValue: {
            currentUser$: of(null),
            logout: () => { }
          }
        }
      ]
    })
      .compileComponents();

    fixture = TestBed.createComponent(Navbar);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
