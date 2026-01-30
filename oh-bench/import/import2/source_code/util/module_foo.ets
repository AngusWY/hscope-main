import { deviceInfo } from '@kit.BasicServicesKit'

export function fun():string{
	return deviceInfo.brand;
}