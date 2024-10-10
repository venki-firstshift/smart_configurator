import { Injectable } from "@angular/core";
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from "rxjs";
import { map } from 'rxjs/operators'
import { WebsocketService } from "./websocket.service";
import { ContextService } from "../context/context.service";

export interface Message {
  filename?: string;
  clientId?: string;
  msg?: Object;
  cmd?: string;
}
function getWsUrl(apiPath) {
  var l = window.location;
  return ((l.protocol === "https:") ? "wss://" : "ws://") + l.host + apiPath;
}


  
@Injectable({providedIn: 'root'})
export class ProcessService {
  //public messages: Subject<Message>;
  // constructor(private wsService: WebsocketService) {
  //   this.clientId = createRandomString(10);
  //   let wsUrl = getWsUrl(`/ws/process/csv/${this.clientId}`);
  //   this.connect(wsUrl)    
  // }
  // private connect(url: string) {
  //   this.messages = <Subject<Message>>this.wsService.connect(url).pipe
  //   (
  //       map((response: MessageEvent): Message => {
  //           let data = JSON.parse(response.data);
  //           return data;
  //       })
  //   )
  // }
 
  constructor(private httpClient: HttpClient, private contextService:ContextService) {
    //console.log("-----> ProcessService <----- ")
  }
  public discoverEntity(fileName:string): Observable<Message> {
    let url = `/api/discover/entity/${this.contextService.clientId}/${fileName}`
    return this.httpClient.post<Message>(url, null)
  }
  public discoverColumns(fileName:string): Observable<Message> {
    let url = `/api/discover/entity/columns/${this.contextService.clientId}/${fileName}`
    return this.httpClient.post<Message>(url, null)
  }
}