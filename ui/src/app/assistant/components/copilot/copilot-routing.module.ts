import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CopilotComponent } from './copilot.component';

@NgModule({
    imports: [RouterModule.forChild([
        { path: '', component: CopilotComponent }
    ])],
    exports: [RouterModule]
})
export class CopilotRoutingModule { }
