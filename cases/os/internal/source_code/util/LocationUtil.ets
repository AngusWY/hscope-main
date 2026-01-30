// PermissionsUtil.ets
import { bundleManager, common, abilityAccessCtrl, PermissionRequestResult, Permissions } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { BusinessError } from '@kit.BasicServicesKit';

const TAG: string = 'ScanKit Permission';
let context = getContext(this) as common.UIAbilityContext;

export class LocationUtil {
  public static async checkAccessToken(permission: Permissions): Promise<abilityAccessCtrl.GrantStatus> {
    let atManager: abilityAccessCtrl.AtManager = abilityAccessCtrl.createAtManager();
    let grantStatus: abilityAccessCtrl.GrantStatus = abilityAccessCtrl.GrantStatus.PERMISSION_DENIED;

    // accessTokenID
    let tokenId: number = 0;
    try {
      let bundleInfo: bundleManager.BundleInfo = await bundleManager.getBundleInfoForSelf(bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_APPLICATION);
      let appInfo: bundleManager.ApplicationInfo = bundleInfo.appInfo;
      tokenId = appInfo.accessTokenId;
    } catch (error) {
      const err: BusinessError = error as BusinessError;
      console.error(`Failed to get bundle info for self. Code is ${err.code}, message is ${err.message}`);
    }

    // 
    try {
      grantStatus = await atManager.checkAccessToken(tokenId, permission);
    } catch (error) {
      const err: BusinessError = error as BusinessError;
      console.error(`Failed to check access token. Code is ${err.code}, message is ${err.message}`);
    }

    return grantStatus;
  }

  public static async reqPermissionsFromUser(): Promise<number[]> {
    const permissions: Array<Permissions> = ['ohos.permission.LOCATION','ohos.permission.APPROXIMATELY_LOCATION'];
    let atManager: abilityAccessCtrl.AtManager = abilityAccessCtrl.createAtManager();
    // requestPermissionsFromUser
    let grantStatus: PermissionRequestResult = { permissions: [], authResults: [] }
    grantStatus = await atManager.requestPermissionsFromUser(context, permissions)// .then((data) => {
    //   let grantStatus: Array<number> = data.authResults;
    //   let length: number = grantStatus.length;
    //   for (let i = 0; i < length; i++) {
    //     if (grantStatus[i] === 0) {
    //       // 
    //     } else {
    //       // 
    //       return;
    //     }
    //   }
    //   // 
    // }).catch((err: BusinessError) => {
    //   console.error(`Failed to request permissions from user. Code is ${err.code}, message is ${err.message}`);
    // })

    return grantStatus.authResults
  }
}

export default new LocationUtil()
