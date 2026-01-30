import { hilog } from "@kit.PerformanceAnalysisKit";

@Component
export struct NewComponent {
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
          hilog.info(0x0000, 'testTag', this.text )
        });
    }
  }
}

