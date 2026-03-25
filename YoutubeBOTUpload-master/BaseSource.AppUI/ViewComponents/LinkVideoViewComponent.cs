using BaseSource.ApiIntegration.WebApi.Setting;
using Microsoft.AspNetCore.Mvc;

namespace BaseSource.AppUI.ViewComponents
{
    public class LinkVideoViewComponent : ViewComponent
    {
        private readonly IConfigSettingApiClient _configSettingApiClient;
        public LinkVideoViewComponent(IConfigSettingApiClient configSettingApiClient)
        {
            _configSettingApiClient = configSettingApiClient;
        }
        public async Task<IViewComponentResult> InvokeAsync()
        {
            var config =  await _configSettingApiClient.GetSetting();
            return View(config.ResultObj);
        }
    }
}
