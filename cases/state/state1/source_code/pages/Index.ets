import { deviceInfo } from '@kit.BasicServicesKit';
import {Child} from "./Child"

@Entry
@Component
struct Index {
  @State message: string = 'Hello World';
  onPageShow(): void {
    this.message = deviceInfo.brand;
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

      Child({taint:this.message})
    }
    .height('100%')
    .width('100%')
  }
}