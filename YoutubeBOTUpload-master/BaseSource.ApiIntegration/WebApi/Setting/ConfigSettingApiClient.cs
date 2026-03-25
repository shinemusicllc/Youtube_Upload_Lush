using BaseSource.ViewModels.Common;
using BaseSource.Shared.Constants;
using BaseSource.ViewModels.Setting;
using BaseSource.Shared.Extensions;

namespace BaseSource.ApiIntegration.WebApi.Setting
{
    public class ConfigSettingApiClient : IConfigSettingApiClient
    {
        private readonly IHttpClientFactory _httpClientFactory;

        public ConfigSettingApiClient(IHttpClientFactory httpClientFactory)
        {
            _httpClientFactory = httpClientFactory;
        }
        public async Task<ApiResult<ConfigSettingVm>> GetSetting()
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<ConfigSettingVm>>("/api/admin/setting");
        }

        public async Task<ApiResult<string>> Update(ConfigSettingVm model)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PostAsync<ApiResult<string>>("/api/admin/setting", model);
        }
    }
}
