@Component
export struct NewComponent {
  private text: string | Resource = '';
  private method: (event?: ClickEvent) => void = (): void => {
  };

  build() {
    Column() {
      Button(this.text)
        .fontSize(20)
        .fontWeight(FontWeight.Normal)
        .align(Alignment.Center)
        .type(ButtonType.Capsule)
        .width('90%')
        .margin({ top: 10, bottom: 5 })
        .onClick(this.method);
    }
  }
}