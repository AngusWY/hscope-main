import { common, Want } from "@kit.AbilityKit";
import { deviceInfo } from "@kit.BasicServicesKit"

@Entry
@Component
struct Index {
  @State message: string = 'Hello World';

  build() {
    RelativeContainer() {
      Button("123").onClick(()=>{
        let context: common.UIAbilityContext = getContext(this) as common.UIAbilityContext;
        let params: Array<Object> = [new Contact("张三", 13344556677)];
        this.message = deviceInfo.brand
        let want: Want = {
          bundleName: "com.ohos.mms",
          abilityName: "com.ohos.mms.MainAbility",
          parameters: {
            contactObjects: JSON.stringify(params),
            pageFlag: "conversation",
            // 
            content: this.message
          }
        };

        context.startAbilityForResult(want).then((data) => {
          console.log("Success" + JSON.stringify(data));
        }).catch(() => {
          console.log("error");
        });
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