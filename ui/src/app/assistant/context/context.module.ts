import { NgModule, ModuleWithProviders } from '@angular/core';
import { ContextService } from './context.service';

@NgModule({
})
export class ContextModule {
    private static isInitialized: boolean = false;

    constructor() {
        // if (!ContextModule.isInitialized) {
        //     throw new Error('call forRoot first');
        // }
    }
    // public static forRoot(): ModuleWithProviders<ContextModule> {
    //     if (this.isInitialized) {
    //         throw new Error('do not call forRoot multiple times');
    //     }
    //     this.isInitialized = true;
    //     return {
    //         ngModule: ContextModule,
    //         providers: [
    //             ContextService,
    //         ],
    //     };
    // }
}