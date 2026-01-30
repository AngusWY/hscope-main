import { hilog } from '@kit.PerformanceAnalysisKit';

@Entry({storage:LocalStorage.getShared()})
@Component
struct Index {
  @State message: string = 'Hello World';
  @LocalStorageLink('PropA') propA: string = "1";
  build() {
    RelativeContainer() {
      Button(this.propA.toString())
        .id('HelloWorld')
        .fontSize(50)
        .fontWeight(FontWeight.Bold)
        .alignRules({
          center: { anchor: '__container__', align: VerticalAlign.Center },
          middle: { anchor: '__container__', align: HorizontalAlign.Center }
        })
        .onClick(()=>{
          hilog.info(0x0000, 'testTag', this.propA);
        })
    }
    .height('100%')
    .width('100%')
  }
}