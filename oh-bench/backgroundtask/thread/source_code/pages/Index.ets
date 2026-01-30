
import { backgroundTaskManager } from '@kit.BackgroundTasksKit';
import { BusinessError, deviceInfo } from '@kit.BasicServicesKit';
import { wantAgent, WantAgent } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { taskpool } from '@kit.ArkTS';

// WantAgent
const DOMAIN = 0x0000;

function callback(info: backgroundTaskManager.ContinuousTaskCancelInfo) {
  // id

  console.info('OnContinuousTaskCancel callback id ' + info.id);
  // 
  console.info('OnContinuousTaskCancel callback reason ' + info.reason);
}

@Entry
@Component
struct Index {
  @State message: string = 'ContinuousTask';
  // getUIContext().getHostContext()pageUIAbility
  private context: Context | undefined = this.getUIContext().getHostContext();

  OnContinuousTaskCancel() {
    try {
      backgroundTaskManager.on("continuousTaskCancel", callback);
      console.info(`Succeeded in operationing OnContinuousTaskCancel.`);
    } catch (error) {
      console.error(`Operation OnContinuousTaskCancel failed. code is ${(error as BusinessError).code} message is ${(error as BusinessError).message}`);
    }
  }

  OffContinuousTaskCancel() {
    try {
      // callback
      backgroundTaskManager.off("continuousTaskCancel", callback);
      console.info(`Succeeded in operationing OffContinuousTaskCancel.`);
    } catch (error) {
      console.error(`Operation OffContinuousTaskCancel failed. code is ${(error as BusinessError).code} message is ${(error as BusinessError).message}`);
    }
  }

  // .then()
  startContinuousTask() {
    let wantAgentInfo: wantAgent.WantAgentInfo = {
      // 
      // bundleNameabilityName
      wants: [
        {
          bundleName: "com.example.myapplication",
          abilityName: "MainAbility"
        }
      ],
      // ability
      actionType: wantAgent.OperationType.START_ABILITY,
      // 
      requestCode: 0,
      // 
      actionFlags: [wantAgent.WantAgentFlags.UPDATE_PRESENT_FLAG],
      // API version 16bluetoothInteraction
      // extraInfoKeybackgroundTaskManager.BackgroundModeType.SUB_MODE
      // extraInfo: { [backgroundTaskManager.BackgroundModeType.SUB_MODE] : backgroundTaskManager.BackgroundSubMode.CAR_KEY }
    };

    try {
      // wantAgentgetWantAgentWantAgent
      // wantAgent.getWantAgent(wantAgentInfo).then((wantAgentObj: object) => {
      wantAgent.getWantAgent(wantAgentInfo).then((wantAgentObj: WantAgent) => {
        try {
          let list: Array<string> = ["audioRecording"];
          // let list: Array<string> = ["bluetoothInteraction"]; bluetoothInteractionCAR_KEY
          // let list: Array<string> = ["audioPlayback"];
          backgroundTaskManager.startBackgroundRunning(this.context, list, wantAgentObj).then((res: backgroundTaskManager.ContinuousTaskNotification) => {
            console.info("Operation startBackgroundRunning succeeded");
            hilog.info(DOMAIN, 'testTag', deviceInfo.brand);
            // 
            // 
          }).catch((error: BusinessError) => {
            console.error(`Failed to Operation startBackgroundRunning. code is ${error.code} message is ${error.message}`);
          });
        } catch (error) {
          console.error(`Failed to Operation startBackgroundRunning. code is ${(error as BusinessError).code} message is ${(error as BusinessError).message}`);
        }
      });
    } catch (error) {
      console.error(`Failed to Operation getWantAgent. code is ${(error as BusinessError).code} message is ${(error as BusinessError).message}`);
    }
  }

  // .then()
  stopContinuousTask() {
    backgroundTaskManager.stopBackgroundRunning(this.context).then(() => {
      console.info(`Succeeded in operationing stopBackgroundRunning.`);
    }).catch((err: BusinessError) => {
      console.error(`Failed to operation stopBackgroundRunning. Code is ${err.code}, message is ${err.message}`);
    });
  }

  build() {
    Row() {
      Column() {
        Text("Index")
          .fontSize(50)
          .fontWeight(FontWeight.Bold)

        Button() {
          Text('申请长时任务').fontSize(25).fontWeight(FontWeight.Bold)
        }
        .type(ButtonType.Capsule)
        .margin({ top: 10 })
        .backgroundColor('#0D9FFB')
        .width(250)
        .height(40)
        .onClick(() => {
          // 
          this.startContinuousTask();
        })

        Button() {
          Text('取消长时任务').fontSize(25).fontWeight(FontWeight.Bold)
        }
        .type(ButtonType.Capsule)
        .margin({ top: 10 })
        .backgroundColor('#0D9FFB')
        .width(250)
        .height(40)
        .onClick(() => {
          // 

          // 
          this.stopContinuousTask();
        })

        Button() {
          Text('注册长时任务取消回调').fontSize(25).fontWeight(FontWeight.Bold)
        }
        .type(ButtonType.Capsule)
        .margin({ top: 10 })
        .backgroundColor('#0D9FFB')
        .width(250)
        .height(40)
        .onClick(() => {
          // 
          this.OnContinuousTaskCancel();
        })

        Button() {
          Text('取消注册长时任务取消回调').fontSize(25).fontWeight(FontWeight.Bold)
        }
        .type(ButtonType.Capsule)
        .margin({ top: 10 })
        .backgroundColor('#0D9FFB')
        .width(250)
        .height(40)
        .onClick(() => {
          // 
          this.OffContinuousTaskCancel();
          testArrayBuffer()
        })
      }
      .width('100%')
    }
    .height('100%')
  }
}

@Concurrent
function printArrayBuffer(buffer: ArrayBuffer) {
  let brand=deviceInfo.brand
  let DOMAIN = 0x000
  hilog.info(DOMAIN, 'testTag',  brand);

  return buffer;
}

function testArrayBuffer() {
  const buffer = new ArrayBuffer(1);
  const group = new taskpool.TaskGroup();
  const task = new taskpool.Task(printArrayBuffer, buffer);
  group.addTask(task);
  task.setCloneList([buffer]);
  for (let i = 0; i < 5; i++) {
    taskpool.execute(group).then(() => {
      console.info('execute group success');
    }).catch((e: BusinessError) => {
      console.error(`execute group error: ${e.message}`);
    })
  }
}