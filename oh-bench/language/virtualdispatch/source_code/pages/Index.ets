import { hilog } from "@kit.PerformanceAnalysisKit";
import { deviceInfo } from "@kit.BasicServicesKit";

@Entry
@Component
struct Index {
  @State message: string = 'Hello World';
  @State counter: number = 0

  build() {
    RelativeContainer() {
      Button("click to leak").onClick(()=>{
        ++this.counter
        let imei = deviceInfo.brand
        let data:NoDataLeak;
        if(this.counter%2 == 0)
          data = new NoDataLeak("no leak");
        else
          data = new DataLeak(imei);

        data.logData();
      })
    }
    .height('100%')
    .width('100%')
  }
}
export class NoDataLeak{
  data:string

  constructor(data:string) {
    this.data = data
  }

  getData():string{
    return this.data;
  }

  logData():void {
    hilog.info(0x0000, 'testTag0', '%{public}s', this.data);
  }
}

export class DataLeak extends NoDataLeak{

  constructor(data:string) {
    super(data)
  }

  logData(): void {
    hilog.info(0x0000, 'testTag1', '%{public}s', super.getData());
  }

}