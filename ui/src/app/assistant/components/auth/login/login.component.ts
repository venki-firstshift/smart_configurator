import { Component } from '@angular/core';
import { map } from 'rxjs/operators'
import { AuthService } from 'src/app/assistant/service/auth.service';
import { LayoutService } from 'src/app/layout/service/app.layout.service';
import { Router } from '@angular/router';
import { AccessToken, ContextService } from 'src/app/assistant/context/context.service';
import { environment } from 'src/environments/environment';

@Component({
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
                private contextService:ContextService,
                private authService: AuthService) { }

    onLogin() {
        //[routerLink]="['/copilot']"
        this.authService.login(this.username, this.password, this.contextService.clientId).subscribe(
            (accessToken:AccessToken) => {
                this.contextService.token = accessToken;
                // console.log("Setting access token clinet id ---> : " + this.contextService.clientId)
                // console.log("Setting access token  : " + this.contextService.token)
                environment.token = accessToken.access_token 
                this.router.navigate(['/copilot'])
            }
        )
    }
}
