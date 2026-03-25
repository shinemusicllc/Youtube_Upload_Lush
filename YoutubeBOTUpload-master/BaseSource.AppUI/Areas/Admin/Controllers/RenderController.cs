using BaseSource.ApiIntegration.WebApi.RenderAdmin;
using BaseSource.ApiIntegration.WebApi.Report;
using BaseSource.ApiIntegration.WebApi.Setting;
using BaseSource.ApiIntegration.WebApi.UserAdmin;
using BaseSource.ViewModels.RenderAdmin;
using Microsoft.AspNetCore.Mvc;

namespace BaseSource.AppUI.Areas.Admin.Controllers
{
    public class RenderController : BaseAdminController
    {
        private readonly IRenderAdminApiClient _renderAdminApiClient;
        private readonly IReportApiClient _reportApiClient;
        private readonly IConfigSettingApiClient _configSettingApiClient;
        private readonly IUserAdminApiClient _userAdminApiClient;

        public RenderController(
            IRenderAdminApiClient renderAdminApiClient
            , IReportApiClient reportApiClient
            , IConfigSettingApiClient configSettingApiClient
            , IUserAdminApiClient userAdminApiClient
            )
        {
            _renderAdminApiClient = renderAdminApiClient;
            _reportApiClient = reportApiClient;
            _configSettingApiClient = configSettingApiClient;
            _userAdminApiClient = userAdminApiClient;
        }
        public async Task<IActionResult> Index()
        {
            var managerChooses = new List<string>();
            string managerSelect = HttpContext.Session.GetString("Manangers");
            if (!string.IsNullOrWhiteSpace(managerSelect))
            {
                managerChooses = managerSelect.Split(",").ToList();
            }
            ViewBag.ManagerChooses = managerChooses;

            var managers = await _userAdminApiClient.GetAllManager();
            if (managers == null || managers.ResultObj == null)
            {
                return NotFound();
            }
            ViewBag.Managers = managers.ResultObj;
            var setting = await _configSettingApiClient.GetSetting();
            if (setting == null)
            {
                return NotFound();
            }
            ViewBag.Setting = setting.ResultObj;
            var report = await _reportApiClient.GeReportAsync(managerSelect ?? string.Empty);

            if (report == null || !report.IsSuccessed)
            {
                return NotFound();

            }

            ViewBag.Report = report.ResultObj;

            var result = await _renderAdminApiClient.GetAllAsync(new RenderAdminRequestDto
            {
                Page = 1,
                PageSize = 2000,
                Managers = User.IsInRole("Admin") ? managerSelect : string.Empty
            });

            if (result == null)
            {
                return NotFound();
            }
            return View(result.ResultObj.Items);
        }

        public async Task<IActionResult> Channel(int channelId, string channelName)
        {
            var managerChooses = new List<string>();
            string managerSelect = HttpContext.Session.GetString("Manangers");
            if (!string.IsNullOrWhiteSpace(managerSelect))
            {
                managerChooses = managerSelect.Split(",").ToList();
            }
            var report = await _reportApiClient.GeReportAsync(managerSelect ?? string.Empty);

            if (report == null || !report.IsSuccessed)
            {
                return NotFound();

            }

            ViewBag.Report = report.ResultObj;
            var result = await _renderAdminApiClient.GetAllByChannelAsync(channelId);
            if (result == null)
            {
                return NotFound();
            }
            ViewBag.ChannelName = channelName;
            return View(result.ResultObj);
        }

        public async Task<IActionResult> RenderInfo(int id)
        {
            var result = await _renderAdminApiClient.GetByIdAsync(id);
            if (result == null || result.ResultObj == null)
            {
                return null;
            }
            return View(result.ResultObj);
        }

        [HttpPost]
        public async Task<IActionResult> Delete()
        {
            var result = await _renderAdminApiClient.DeleteAllAsync();
            return RedirectToAction("Index");
        }

       
    }
}
