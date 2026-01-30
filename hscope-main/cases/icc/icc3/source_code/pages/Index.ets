import { deviceInfo } from '@kit.BasicServicesKit';
import { hilog } from '@kit.PerformanceAnalysisKit';

@Entry
@Component
struct Index {
  @State message: string = 'Hello World';
  aboutToAppear(): void {
    AppStorage.setOrCreate("brand", deviceInfo.brand)
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
          AppStorage.setOrCreate("brand", deviceInfo.brand)
        })
    }
    .height('100%')
    .width('100%')
  }
}

@Component
export struct NewComponent {
  aboutToAppear(): void {
    let taint:string = AppStorage.Get("brand") as string
    hilog.info(0x0000, 'testTag', taint )
  }
  private text: string = '';
  build() {
    Column() {
      Button(this.text)
        .fontSize(20)
        .fontWeight(FontWeight.Normal)
        .align(Alignment.Center)
        .type(ButtonType.Capsule)
        .width('90%')
        .margin({ top: 10, bottom: 5 })
        .onClick(()=>{
          let taint:string = AppStorage.Get("brand") as string
          hilog.info(0x0000, 'testTag', taint )
        });
    }
  }
}