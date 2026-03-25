using BaseSource.ApiIntegration.WebApi.ManagerBOT;
using BaseSource.ApiIntegration.WebApi.Report;
using BaseSource.ApiIntegration.WebApi.UserAdmin;
using BaseSource.ViewModels.ManagerBOT;
using Microsoft.AspNetCore.Mvc;

namespace BaseSource.AppUI.Areas.Admin.Controllers
{
    public class ManagerBOTController : BaseAdminController
    {
        private readonly IManagerBOTApiClient _managerBOTApiClient;
        private readonly IReportApiClient _reportApiClient;
        private readonly IUserAdminApiClient _userAdminApiClient;
        public ManagerBOTController(
            IManagerBOTApiClient managerBOTApiClient
            , IReportApiClient reportApiClient
            , IUserAdminApiClient userAdminApiClient
            )
        {
            _managerBOTApiClient = managerBOTApiClient;
            _reportApiClient = reportApiClient;
            _userAdminApiClient = userAdminApiClient;
        }

        [HttpGet]
        public async Task<IActionResult> Index()
        {
            var managerChooses = new List<string>();
            string managerSelect = HttpContext.Session.GetString("Manangers");
            if (!string.IsNullOrWhiteSpace(managerSelect))
            {
                managerChooses = managerSelect.Split(",").ToList();
            }

            ViewBag.ManagerChooses = managerChooses;
            var report = await _reportApiClient.GeReportAsync(managerSelect ?? string.Empty);

            if (report == null || !report.IsSuccessed)
            {
                return NotFound();

            }

            ViewBag.Report = report.ResultObj;
            var result = await _managerBOTApiClient.GetBOTByFilterAsync(new ManagerBOTRequestDto
            {
                Page = 1,
                PageSize = 200,
                Managers = User.IsInRole("Admin") ? managerSelect : string.Empty
            });

            var managers = await _userAdminApiClient.GetAllManager();
            if (managers == null || managers.ResultObj == null)
            {
                return NotFound();
            }
            ViewBag.Managers = managers.ResultObj;
            if (result == null || result.ResultObj == null)
            {
                return NotFound();
            }
            return View(result.ResultObj.Items);
        }

        [HttpPost]
        [Route("/admin/bot/update")]
        public async Task<IActionResult> Update(ManagerBotUpdateDto model)
        {
            var result = await _managerBOTApiClient.UpdateBOTAsync(model.Id, model);
            return RedirectToAction("Index");
        }

        [HttpPost]
        public async Task<IActionResult> Delete(int id)
        {
            var result = await _managerBOTApiClient.DeleteAsync(id);
            return RedirectToAction("Index");
        }

        [HttpGet]
        [Route("/admin/bot/user")]
        public async Task<IActionResult> BotOfUser(string userId, string username)
        {
            if (string.IsNullOrEmpty(userId) || string.IsNullOrEmpty(username))
            {
                return NotFound();
            }
            ViewBag.UserId = userId;
            ViewBag.UserName = username;
            var result = await _managerBOTApiClient.GetBotByUserIdAsync(userId);

            if (result == null || result.ResultObj == null)
            {
                return NotFound();
            }

            return View(result.ResultObj);
        }

        [HttpGet]
        [Route("/admin/bot/userofbot")]
        public async Task<IActionResult> UserOfBot(int botId, string botName)
        {

            ViewBag.BotId = botId;
            ViewBag.BotName = botName;
            var result = await _managerBOTApiClient.GetUserOfBotIdAsync(botId);

            if (result == null || result.ResultObj == null)
            {
                return NotFound();
            }

            return View(result.ResultObj);
        }
        [HttpPost]
        [Route("/admin/bot/updateThread")]
        public async Task<IActionResult> UpdateThread(BotUpdateThreadDto model)
        {
            var result = await _managerBOTApiClient.UpdateThreadAsync(model);
            return RedirectToAction("Index");
        }
    }
}
