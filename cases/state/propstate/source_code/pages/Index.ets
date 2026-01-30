import { deviceInfo } from '@kit.BasicServicesKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { CountDownComponent } from './CountDownComponent';

const DOMAIN = 0x0000;


@Entry
@Component
struct Index {
  @State tmsg: string = "10";
 onPageShow(): void {
   this.tmsg = deviceInfo.brand
 }
  build() {
    Column() {
      Text(`Grant ${this.tmsg} nuggets to play.`)
      // 
      Button(`+1 - Nuggets in New Game`).onClick(() => {
        this.tmsg = deviceInfo.brand
      })
      CountDownComponent({ count: this.tmsg, costOfOneAttempt: 2 })
    }
  }
}

