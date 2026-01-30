//

import { AsyncCallback, BusinessError } from '@kit.BasicServicesKit';
import { hilog } from '@kit.PerformanceAnalysisKit';

// function fun1(a0: any):void{
//   a0.on()
// }

//%mm1
//access.on(statechange, %mm1)

//data accessdata
//%vv1 = access.data or  %vv1 = access()

//call mm1(%vv1)

// fun1(access)
// 
import { access } from '@kit.ConnectivityKit';
export function enable():void {
  access.enableBluetooth();
  access.on('stateChange', (data) => {
    let btStateMessage = '';
    switch (data) {
      case 0:
        btStateMessage += 'STATE_OFF';
        break;
      case 1:
        btStateMessage += 'STATE_TURNING_ON';
        break;
      case 2:
        btStateMessage += 'STATE_ON';
        break;
      default:
        btStateMessage += 'unknown status';
        break;
    }
    if (btStateMessage == 'STATE_ON') {
      access.off('stateChange');
    }
    console.info('bluetooth statues: ' + btStateMessage);
  })
}
// 
const DOMAIN = 0x0000;
export function disable():void {

  try {
    access.disableBluetooth();
  } catch (err) {
    hilog.error(DOMAIN, "blutooth", 'errCode: ' + (err as BusinessError).code + ', errMessage: ' + (err as BusinessError).message);
  }
  // statechange
  access.on('stateChange', (data) => {
    let btStateMessage = '';
    switch (data) {
      case 0:
        btStateMessage += 'STATE_OFF';
        break;
      case 1:
        btStateMessage += 'STATE_TURNING_ON';
        break;
      case 2:
        btStateMessage += 'STATE_ON';
        break;
      case 3:
        btStateMessage += 'STATE_TURNING_OFF';
        break;
      case 4:
        btStateMessage += 'STATE_BLE_TURNING_ON';
        break;
      case 5:
        btStateMessage += 'STATE_BLE_ON';
        break;
      case 6:
        btStateMessage += 'STATE_BLE_TURNING_OFF';
        break;
      default:
        btStateMessage += 'unknown status';
        break;
    }
    if (btStateMessage == 'STATE_OFF') {
      access.off('stateChange');
    }
    console.info("bluetooth statues: " + btStateMessage);
  })
}