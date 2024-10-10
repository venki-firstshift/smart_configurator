import { Injectable } from '@angular/core';

export interface AccessToken {
    access_token: string;
    token_type: string
}

function createRandomString(length) {
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let result = "";
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }
  
@Injectable({ providedIn: 'root'})
export class ContextService {
    public clientId:string;
    public token: AccessToken;
    constructor() { 
      this.clientId = createRandomString(10);
        //console.log(`---- constructor gets called -- ${this.clientId} ------ `)
    }
}