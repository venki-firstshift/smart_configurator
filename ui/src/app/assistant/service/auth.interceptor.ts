import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { ContextService } from '../context/context.service';

@Injectable()
export class JwtInterceptor implements HttpInterceptor {
    constructor(private contextService: ContextService) { 
        //console.log("-----> JwtInterceptor <----- ")
    }

    intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        // add auth header with jwt if account is logged in and request is to the api url
        // console.log("Interceptor Token is : -----> " + this.contextService.token)
        // console.log("Interceptor  clinet id ---> : " + this.contextService.clientId)
                
        //let authToken = environment.token
        let authToken = this.contextService.token?.access_token
        const isApiUrl = request.url.startsWith(environment.apiUrl);
        if (authToken && isApiUrl) {
            request = request.clone({
                setHeaders: { Authorization: `Bearer ${authToken}` }
            });
        }

        return next.handle(request);
    }
}

 