import { Component } from '@angular/core';
import { AuthService } from 'src/app/assistant/service/auth.service';
import { LayoutService } from 'src/app/layout/service/app.layout.service';
import { Router } from '@angular/router';

@Component({
    providers: [AuthService, LayoutService],
    selector: 'app-login',
    templateUrl: './login.component.html',
    styles: [`
        :host ::ng-deep .pi-eye,
        :host ::ng-deep .pi-eye-slash {
            transform:scale(1.6);
            margin-right: 1rem;
            color: var(--primary-color) !important;
        }
    `]
})
export class LoginComponent {

    valCheck: string[] = ['remember'];

    password!: string;
    username!: string;

    constructor(private router: Router,
                public layoutService: LayoutService, 
                private authService: AuthService) { }

    onLogin() {
        //[routerLink]="['/copilot']"
        this.router.navigate(['/copilot'])
    }
}
