import { deviceInfo } from '@kit.BasicServicesKit';

let deviceTypeInfo = deviceInfo.deviceType;
// the value of the deviceType is :wearable
console.info('the value of the deviceType is :' + deviceTypeInfo);



let dI: Record<string, string> = {
  "deviceType": deviceInfo.deviceType,
  "manufacture":deviceInfo.manufacture,
  "brand":deviceInfo.brand,
  "marketName":deviceInfo.marketName
}
export function getdi(key:string):string{
  return dI[key]
}