using BaseSource.ApiIntegration.WebApi.Setting;
using Microsoft.AspNetCore.Mvc;

namespace BaseSource.AppUI.Controllers
{
    public class HomeController : BaseController
    {
        public readonly IConfigSettingApiClient _configSettingApiClient;
        public HomeController(IConfigSettingApiClient configSettingApiClient)
        {
            _configSettingApiClient = configSettingApiClient;
        }
        public IActionResult Index()
        {
            if (User.IsInRole("Manager") || User.IsInRole("Admin"))
            {
                return Redirect("/admin/user/index");
            }
            return Redirect("/render/create");
            // return View();
        }
        public async Task<IActionResult> Contact()
        {
            var result =await _configSettingApiClient.GetSetting();
            return View(result.ResultObj);
        }
    }
}
