using BaseSource.ApiIntegration.WebApi.ChannelAdmin;
using BaseSource.ApiIntegration.WebApi.Report;
using BaseSource.ApiIntegration.WebApi.UserAdmin;
using BaseSource.ViewModels.ChannelAdmin;
using BaseSource.ViewModels.UserAdmin;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using OfficeOpenXml;

namespace BaseSource.AppUI.Areas.Admin.Controllers
{
    public class ChannelController : BaseAdminController
    {
        private readonly IChannelAdminApiClient _channelAdminApiClient;
        private readonly IReportApiClient _reportApiClient;
        private readonly IUserAdminApiClient _userAdminApiClient;
        public ChannelController(
            IChannelAdminApiClient channelAdminApiClient
            , IReportApiClient reportApiClient
            , IUserAdminApiClient userAdminApiClient
            )
        {
            _channelAdminApiClient = channelAdminApiClient;
            _reportApiClient = reportApiClient;
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
            var report = await _reportApiClient.GeReportAsync(managerSelect ?? string.Empty);

            if (report == null || !report.IsSuccessed)
            {
                return NotFound();

            }

            ViewBag.Report = report.ResultObj;
            var result = await _channelAdminApiClient.GetAllAsync(new ChannelAdminRequestDto
            {
                Page = 1,
                PageSize = 2500,
                Managers = User.IsInRole("Admin") ? managerSelect : string.Empty
            });
            if (result == null || result.ResultObj == null)
            {
                return NotFound();
            }

            var managers = await _userAdminApiClient.GetAllManager();
            if (managers == null || managers.ResultObj == null)
            {
                return NotFound();
            }
            ViewBag.Managers = managers.ResultObj;
            return View(result.ResultObj.Items);
        }

        [HttpGet]
        [Route("/admin/channel/user")]
        public async Task<IActionResult> ChannelUser(string userId, string username)
        {
            if (string.IsNullOrEmpty(userId) || string.IsNullOrEmpty(username))
            {
                return NotFound();
            }
            var result = await _channelAdminApiClient.GetAllByUserIdAsync(userId);
            if (result == null)
            {
                return NotFound();
            }
            ViewBag.UserId = userId;
            ViewBag.UserName = username;
            return View(result.ResultObj);
        }

        [HttpGet]
        [Route("/admin/channel/bot")]
        public async Task<IActionResult> ChannelOfBot(int botId, string botName)
        {

            var result = await _channelAdminApiClient.GetChannelByBotIdAsync(botId);
            if (result == null)
            {
                return NotFound();
            }
            ViewBag.BotId = botId;
            ViewBag.BotName = botName;
            return View(result.ResultObj);
        }

        [HttpGet]
        [Route("/admin/channel/users")]
        public async Task<IActionResult> UserChannel(int channelId, string channelName)
        {

            var result = await _channelAdminApiClient.GetUserOfChannelIdAsync(channelId);
            if (result == null)
            {
                return NotFound();
            }
            ViewBag.ChannelId = channelId;
            ViewBag.ChannelName = channelName;

            var users = await _userAdminApiClient.GetUserByFilter(
                new UserAdminRequestDto
                {
                    Page = 1,
                    PageSize = 1000
                });
            if (users == null)
            {
                return NotFound();
            }
            ViewBag.Users = users.ResultObj.Items;
            return View(result.ResultObj);
        }

        [HttpPost]
        [Route("/admin/channel/UpdateUserChannel")]
        public async Task<IActionResult> UpdateUserChannel(UpdateUserChannelDto model)
        {
            var result = await _channelAdminApiClient.UpdateChannelOfUser(model);
            if (result == null || !result.IsSuccessed)
            {
                return RedirectToAction("ChannelUser", new { userId = model.UserId, username = model.UserName, message = result?.Message ?? "Cập nhật không thành công!" });
            }
            return RedirectToAction("ChannelUser", new { userId = model.UserId, username = model.UserName });
        }

        [HttpPost]
        [Route("/admin/channel/addUser")]
        public async Task<IActionResult> AddUserToChannel(UpdateUserChannelDto model, string channelName)
        {
            var result = await _channelAdminApiClient.UpdateChannelOfUser(model);
            if (result == null || !result.IsSuccessed)
            {
                return RedirectToAction("UserChannel", new { channelId = model.ChannelId, channelName = channelName, message = result?.Message ?? "Cập nhật không thành công!" });
            }
            return RedirectToAction("UserChannel", new { channelId = model.ChannelId, channelName = channelName });
        }

        [HttpPost]
        [AllowAnonymous]
        public async Task<IActionResult> UpdateProfile(int id)
        {
            var result = await _channelAdminApiClient.UpdateProfileAsync(id);
            return Json(string.Empty);
        }

        [HttpGet]
        public async Task<IActionResult> Export()
        {
            var result = await _channelAdminApiClient.GetAllReportAsync();
            if (result == null)
            {
                return NotFound();
            }
            var data = result.ResultObj;

            var stream = new MemoryStream();

            // Tạo một đối tượng ExcelPackage
            ExcelPackage.LicenseContext = LicenseContext.NonCommercial;
            using (ExcelPackage xlPackage = new ExcelPackage(stream))
            {
                // Tạo một trang tính mới
                ExcelWorksheet worksheet = xlPackage.Workbook.Worksheets.Add("My Worksheet");

                // Điền tiêu đề cho các cột
                worksheet.Cells["A1"].Value = "Avatar";
                worksheet.Cells["B1"].Value = "ChannelName";
                worksheet.Cells["C1"].Value = "ChannelYTId";
                worksheet.Cells["D1"].Value = "ChannelLink";
                worksheet.Cells["E1"].Value = "BotName";
                worksheet.Cells["F1"].Value = "ChannelGmail";
                worksheet.Cells["G1"].Value = "Group";
                worksheet.Cells["H1"].Value = "CreatedTime";
                worksheet.Cells["I1"].Value = "TotalUser";
                worksheet.Cells["J1"].Value = "Status";
                worksheet.Cells["K1"].Value = "User Upload";
                worksheet.Cells["L1"].Value = "Manager";

                // Điền dữ liệu vào các ô
                int row = 2;
                foreach (var person in data)
                {
                    worksheet.Cells[string.Format("A{0}", row)].Value = person.Avatar;
                    worksheet.Cells[string.Format("B{0}", row)].Value = person.ChannelName;
                    worksheet.Cells[string.Format("C{0}", row)].Value = person.ChannelYTId;
                    worksheet.Cells[string.Format("D{0}", row)].Value = person.ChannelLink;
                    worksheet.Cells[string.Format("E{0}", row)].Value = person.BotName;
                    worksheet.Cells[string.Format("F{0}", row)].Value = person.ChannelGmail;
                    worksheet.Cells[string.Format("G{0}", row)].Value = person.Group;
                    worksheet.Cells[string.Format("H{0}", row)].Value = person.CreatedTime.ToString("dd/MM/yyyy HH:mm:ss");
                    worksheet.Cells[string.Format("I{0}", row)].Value = person.TotalUser;
                    worksheet.Cells[string.Format("J{0}", row)].Value = person.Status;
                    var userUploads = string.Empty;
                    if (person.UserJoins != null && person.UserJoins.Any())
                    {
                        userUploads = string.Join(",", person.UserJoins);
                    }
                    worksheet.Cells[string.Format("K{0}", row)].Value = userUploads;
                    worksheet.Cells[string.Format("L{0}", row)].Value = person.UserManager;
                    row++;
                }
                xlPackage.Workbook.Properties.Title = "Export Channel Youtube";
                xlPackage.Workbook.Properties.Author = "Export Channel Youtube";

                await xlPackage.SaveAsync();
                stream.Position = 0;
                return File(stream, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "bao-cao-channel-youtube.xlsx");
            }
        }
        [HttpGet]

        public async Task<IActionResult> Delete(int channelId)
        {
            var result = await _channelAdminApiClient.DeleteAsync(channelId);
            return RedirectToAction("Index");
        }
        public async Task<IActionResult> DeleteAjax(int id)
        {
            var result = await _channelAdminApiClient.DeleteAsync(id);
            return Json(string.Empty);
        }
    }
}
