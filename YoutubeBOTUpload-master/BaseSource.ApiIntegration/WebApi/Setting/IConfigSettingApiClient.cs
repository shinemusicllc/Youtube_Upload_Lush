using BaseSource.ViewModels.Common;
using BaseSource.ViewModels.Setting;

namespace BaseSource.ApiIntegration.WebApi.Setting
{
    public interface IConfigSettingApiClient
    {
        Task<ApiResult<ConfigSettingVm>> GetSetting();
        Task<ApiResult<string>> Update(ConfigSettingVm model); 
    }
}