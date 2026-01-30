@Component
export struct leafcomponent {
  @Link tmp: string
  private func: (msg: string) => void = (): void => {
  };
  build() {
    RelativeContainer() {
      Text(this.tmp)
        .id('HelloWorld')
        .fontSize($r('app.float.page_text_font_size'))
        .fontWeight(FontWeight.Bold)
        .alignRules({
          center: { anchor: '__container__', align: VerticalAlign.Center },
          middle: { anchor: '__container__', align: HorizontalAlign.Center }
        })
        .onClick(()=>{
          this.func(this.tmp)
        })

    }
    .height('100%')
    .width('100%')
  }
}