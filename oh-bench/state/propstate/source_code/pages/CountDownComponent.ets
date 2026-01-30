import { hilog } from "@kit.PerformanceAnalysisKit";
const DOMAIN = 0x0000;

@Component
export struct CountDownComponent {
  @Prop count: string = "abc";
  costOfOneAttempt: number = 1;

  build() {
    Column() {
      if (this.costOfOneAttempt > 0) {
        Text(`You have ${this.count} Nuggets left`)
      } else {
        Text('Game over!')
      }
      // @Prop
      Button(`Try again`).onClick(() => {
        hilog.info(DOMAIN, 'testTag', this.count);
      })
    }
  }
}
