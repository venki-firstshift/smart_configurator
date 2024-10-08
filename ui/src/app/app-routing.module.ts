import { RouterModule } from '@angular/router';
import { NgModule } from '@angular/core';
import { NotfoundComponent } from './assistant/components/notfound/notfound.component';
import { AppLayoutComponent } from "./layout/app.layout.component";

@NgModule({
    imports: [
        RouterModule.forRoot([
            {
                path: 'copilot', component: AppLayoutComponent,
                children: [
                    { path: '', loadChildren: () => import('./assistant/components/copilot/copilot.module').then(m => m.CopilotModule) }
                ]
            },
            { path: 'auth', loadChildren: () => import('./assistant/components/auth/auth.module').then(m => m.AuthModule) },
            { path: 'notfound', component: NotfoundComponent },
            { path: '', redirectTo: '/auth/login' , pathMatch: "full"},
            { path: '**', redirectTo: '/notfound' },
        ], { scrollPositionRestoration: 'enabled', anchorScrolling: 'enabled', onSameUrlNavigation: 'reload' })
    ],
    exports: [RouterModule]
})
export class AppRoutingModule {
}
