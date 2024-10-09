import { Injectable } from "@angular/core";
import { Subject } from "rxjs";
import { map } from 'rxjs/operators'
import { WebsocketService } from "./websocket.service";

export interface Message {
  filename?: string;
  clientId?: string;
  msg?: Object;
  cmd?: string;
}
function createRandomString(length) {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}
function getWsUrl(apiPath) {
  var l = window.location;
  return ((l.protocol === "https:") ? "wss://" : "ws://") + l.host + apiPath;
}


  
@Injectable()
export class ProcessService {
  public messages: Subject<Message>;
  public clientId: string;
  constructor(private wsService: WebsocketService) {
    this.clientId = createRandomString(10);
    let wsUrl = getWsUrl(`/ws/process/csv/${this.clientId}`);
    this.connect(wsUrl)    
  }
  private connect(url: string) {
    this.messages = <Subject<Message>>this.wsService.connect(url).pipe
    (
        map((response: MessageEvent): Message => {
            let data = JSON.parse(response.data);
            return data;
        })
    )
  }
}