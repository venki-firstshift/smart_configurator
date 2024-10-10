import { NgModule } from '@angular/core';
import { LocationStrategy, PathLocationStrategy } from '@angular/common';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { AppLayoutModule } from './layout/app.layout.module';
import { NotfoundComponent } from './assistant/components/notfound/notfound.component';
import { JwtInterceptor } from './assistant/service/auth.interceptor';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { ContextService } from './assistant/context/context.service';
import { AuthService } from './assistant/service/auth.service';
import { ProcessService } from './assistant/service/process.service';
@NgModule({
    declarations: [AppComponent, NotfoundComponent],
    imports: [
        AppRoutingModule, 
        AppLayoutModule
    ],
    providers: [
        ContextService,
        { provide: HTTP_INTERCEPTORS, useClass: JwtInterceptor, multi: true, deps: [ContextService]},
        { provide: LocationStrategy, useClass: PathLocationStrategy }
    ],
    bootstrap: [AppComponent],
})
export class AppModule {}
