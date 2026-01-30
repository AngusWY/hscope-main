import {NewComponent} from "./NewComponent"
import { deviceInfo } from "@kit.BasicServicesKit";
import { hilog } from "@kit.PerformanceAnalysisKit";

@Entry
@Component
struct Index {
  @State message: string = 'Hello World';

  func(){
    let taint = deviceInfo.brand
    hilog.info(0x0000, 'testTag', taint )
  }

  build() {
    RelativeContainer() {
      Text(this.message)
        .id('HelloWorld')
        .fontSize($r('app.float.page_text_font_size'))
        .fontWeight(FontWeight.Bold)
        .alignRules({
          center: { anchor: '__container__', align: VerticalAlign.Center },
          middle: { anchor: '__container__', align: HorizontalAlign.Center }
        })
        .onClick(() => {
          this.message = 'Welcome';
        })
      NewComponent({method: () => {
        this.func();}})
    }
    .height('100%')
    .width('100%')
  }
}