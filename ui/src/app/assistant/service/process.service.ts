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
  
@Injectable()
export class ProcessService {
  public messages: Subject<Message>;
  public clientId: string;
  constructor(private wsService: WebsocketService) {
    this.clientId = createRandomString(10);
    let wsUrl = `ws://localhost:8000/ws/process/csv/${this.clientId}`;
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