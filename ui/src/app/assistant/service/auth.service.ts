import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators'
import { AccessToken, ContextService } from '../context/context.service';
import { environment } from '../../../environments/environment';
// interface OAuth2Form {
//     grant_type:string = "password";
//     username: string;
//     password: string;
//     scope: string = "something";
//     client_id: string;
//     client_secret: string = "no secret";
// }

@Injectable({providedIn: 'root'})
export class AuthService {
    constructor(private httpClient: HttpClient, private contextService:ContextService ) { 
        //console.log("-----> AuthService <----- ")
    }

    public login(userName:string, password:string, clientId:string):Observable<AccessToken> {
        let data = { 
            grant_type: "password",
            username: userName,
            password: password,
            scope: "something",
            client_id: clientId,
            client_secret: "no secret"
        }
        let httpParams = new URLSearchParams(data)
        let httpOptions = {headers: new HttpHeaders({ 'Content-Type': 'application/x-www-form-urlencoded' })};
        let url = "/api/token"
        return this.httpClient.post<AccessToken>(url, httpParams, httpOptions)
    }
}