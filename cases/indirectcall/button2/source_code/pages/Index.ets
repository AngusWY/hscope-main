import { common, Want } from '@kit.AbilityKit';
import { deviceInfo } from '@kit.BasicServicesKit'
@Entry
@Component
struct Index {
  @State brand: string = 'Hello World';

  build() {
    Column() {
      Button("1234546").onClick(()=>{
        this.brand = deviceInfo.brand
      })
      Button("2").onClick(()=>{
        let context: common.UIAbilityContext = getContext(this) as common.UIAbilityContext;
        let params: Array<Object> = [new Contact("张三", 13344556677)];
        let imei = "imei"
        let want: Want = {
          bundleName: "com.ohos.mms",
          abilityName: "com.ohos.mms.MainAbility",
          parameters: {
            contactObjects: JSON.stringify(params),
            pageFlag: "conversation",
            // 
            content: this.brand
          }
        };
        console.log("Success" + JSON.stringify(want));
        context.startAbilityForResult(want)
      })




    }
    .height('100%')
    .width('100%')
  }
}

export class Contact {
  contactsName: string;
  telephone: number;

  constructor(contactsName: string, telephone: number) {
    this.contactsName = contactsName;
    this.telephone = telephone;
  }
}