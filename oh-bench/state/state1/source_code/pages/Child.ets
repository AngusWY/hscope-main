import { deviceInfo } from '@kit.BasicServicesKit';
import { hilog } from '@kit.PerformanceAnalysisKit';

@Component
export struct Child {
  @State taint: string = 'Hello World';
  func1(){
    hilog.info(0x0000, 'testTag', this.taint )
  }
  build() {
    RelativeContainer() {
      Text(this.taint)
        .id('HelloWorld')
        .fontSize($r('app.float.page_text_font_size'))
        .fontWeight(FontWeight.Bold)
        .alignRules({
          center: { anchor: '__container__', align: VerticalAlign.Center },
          middle: { anchor: '__container__', align: HorizontalAlign.Center }
        })
        .onClick(() => {
          this.func1()
        })
    }
    .height('100%')
    .width('100%')
  }
}