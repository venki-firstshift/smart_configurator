import { Component, OnInit, OnDestroy } from '@angular/core';

import { FileUploadEvent } from 'primeng/fileupload';
import { Subscription, debounceTime, map } from 'rxjs';
import { LayoutService } from 'src/app/layout/service/app.layout.service';
import { WebsocketService } from '../../service/websocket.service';
import { Message, ProcessService } from '../../service/process.service';
import { ContextService } from '../../context/context.service';

export interface DiscoveryStep {
    stepName: string;
    state?: string; // progress, success, error
    nextStepName?: string
}
@Component({
    templateUrl: './copilot.component.html',
})
export class CopilotComponent implements OnInit, OnDestroy {

    subscription!: Subscription;
    fileName: string;
    entity:Object;
    mappings:Array<Object>;

    public steps:Map<string, DiscoveryStep> = new Map<string, DiscoveryStep>(
        [
            ["entity", { "stepName": "entity", "nextStepName": "columns"}], 
            ["columns", { "stepName": "columns"}]
        ]
    );

    constructor(public contextService:ContextService, public layoutService: LayoutService, private processService: ProcessService) {
        //console.log("-----> CopilotComponent <----- ")
        this.subscription = this.layoutService.configUpdate$
        .pipe(debounceTime(25)).subscribe((config) => {});
        // this.processService.messages.subscribe((serverMsg: Message) => {
        //     console.log(serverMsg.msg);

        //     this.steps.get(serverMsg.cmd).state = 'success'
        //     let nextStep = this.steps.get(serverMsg.cmd).nextStepName
        //     if (nextStep) {
        //         this.steps.get(nextStep).state = 'ready'
        //     }
        //     if (serverMsg.cmd == 'entity') {
        //         this.entity = serverMsg.msg["CONFIG_DATA_ENTITY"]
        //     } else if (serverMsg.cmd == 'columns') {
        //         this.mappings = serverMsg.msg["CONFIG_DATA_ENTITY_MAP"]
        //     }
        // });
        
    }

    ngOnInit() {
    }
    onUpload($event: FileUploadEvent) {
        var webSocketId:Number = $event.originalEvent["body"]["client_id"] 
        console.log(webSocketId)
        console.log("Work once uploaded!")
        let fileName = $event.originalEvent["body"]["filename"]
        this.fileName = fileName
        this.steps.get('entity').state = 'ready'

        this.entity = null;
        this.mappings = null;

    }
    onDiscoverEntity($event) {
        this.steps.get('entity').state = 'progress'
        this.processService.discoverEntity(this.fileName).subscribe(serverMsg => {
            this.steps.get(serverMsg.cmd).state = 'success'
            let nextStep = this.steps.get(serverMsg.cmd).nextStepName
            if (nextStep) {
                this.steps.get(nextStep).state = 'ready'
            }
            this.entity = serverMsg.msg["CONFIG_DATA_ENTITY"]
        })
    }
    onDiscoverEntityMap($event) {
        this.steps.get('columns').state = 'progress'
        this.processService.discoverColumns(this.fileName).subscribe(serverMsg => {
            this.steps.get(serverMsg.cmd).state = 'success'
            let nextStep = this.steps.get(serverMsg.cmd).nextStepName
            if (nextStep) {
                this.steps.get(nextStep).state = 'ready'
            }
            this.entity = serverMsg.msg["CONFIG_DATA_ENTITY"]
            this.mappings = serverMsg.msg["CONFIG_DATA_ENTITY_MAP"]
        })
    }
    // sendCommand(msg: Message) {
    //     this.steps.get(msg.cmd).state = 'progress'
    //     this.processService.messages.next(msg);
    // }
    ngOnDestroy() {
        if (this.subscription) {
            this.subscription.unsubscribe();
        }
    }
    public get clientId(): string {
        return this.contextService.clientId
    }
    public get headers(): Array<string> {
        if (this.mappings != null && this.mappings.length > 0) {
            let mapping = this.mappings[0]
            let hdrs = Object.keys(mapping)
            console.log(hdrs)
            return hdrs;
        } else {
            return null;
        }
    }
}
