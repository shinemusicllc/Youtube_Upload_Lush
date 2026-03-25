using BaseSource.ApiIntegration.WebApi.Channel;
using BaseSource.ApiIntegration.WebApi.Render;
using BaseSource.Shared.Constants;
using BaseSource.ViewModels.Render;
using BaseSource.ViewModels.RenderAdmin;
using Microsoft.AspNetCore.Mvc;

namespace BaseSource.AppUI.Controllers
{
    public class RenderController : BaseController
    {
        private readonly IRenderApiClient _renderApiClient;
        private readonly IChannelApiClient _channelApiClient;

        public RenderController(
            IRenderApiClient renderApiClient
            , IChannelApiClient channelApiClient)
        {
            _renderApiClient = renderApiClient;
            _channelApiClient = channelApiClient;
        }


        public async Task<IActionResult> Index()
        {
            var renders = await _renderApiClient.GetAllAsync(new RenderRequestDto
            {
                Page = 1,
                PageSize = 500
            });
            if (renders == null)
            {
                return NotFound();
            }
            return View();
        }
        [HttpGet]
        public async Task<IActionResult> Create()
        {

            var renders = await _renderApiClient.GetAllAsync(new RenderRequestDto
            {
                Page = 1,
                PageSize = 5000
            });

            var channels = await _channelApiClient.GetChannelByUserAsync();

            if (renders == null || channels == null)
            {
                return NotFound();
            }
            ViewBag.Channels = channels.ResultObj;
            ViewBag.Renders = renders.ResultObj.Items;

            var reports = await _renderApiClient.ReportAsync();
            if (reports == null || reports.ResultObj == null)
            {
                return null;
            }
            ViewBag.Report = reports.ResultObj;
            return View();
        }

        [HttpPost]
        public async Task<IActionResult> Create(RenderCreateDto model)
        {


            if (!ModelState.IsValid)
            {
                var errorList = ModelState
                .Where(x => x.Value.Errors.Count > 0)
                .ToDictionary(
                    kvp => kvp.Key,
                    kvp => kvp.Value.Errors.Select(e => e.ErrorMessage).ToArray()
                );
                ModelState.AddModelError("", errorList.FirstOrDefault().Value.FirstOrDefault());

                var renders = await _renderApiClient.GetAllAsync(new RenderRequestDto
                {
                    Page = 1,
                    PageSize = 500
                });

                var channels = await _channelApiClient.GetChannelByUserAsync();

                if (renders == null || channels == null)
                {
                    return NotFound();
                }
                ViewBag.Channels = channels.ResultObj;
                ViewBag.Renders = renders.ResultObj.Items;

                var reports = await _renderApiClient.ReportAsync();
                if (reports == null || reports.ResultObj == null)
                {
                    return null;
                }
                ViewBag.Report = reports.ResultObj;
                return View(model);

            }

            var arrayTime = model.TimeRenderString.Split(":").Select(x => int.Parse(x)).ToList();
            model.TimeRender = new TimeSpan(arrayTime[0], arrayTime[1], arrayTime[2]);

            var result = await _renderApiClient.CreateAsync(model);
            if (result == null || !result.IsSuccessed)
            {
                ModelState.AddModelError("", result?.Message ?? "Không thể tạo luồng stream!");

                var renders = await _renderApiClient.GetAllAsync(new RenderRequestDto
                {
                    Page = 1,
                    PageSize = 500
                });

                var channels = await _channelApiClient.GetChannelByUserAsync();

                if (renders == null || channels == null)
                {
                    return NotFound();
                }
                ViewBag.Channels = channels.ResultObj;
                ViewBag.Renders = renders.ResultObj.Items;

                var reports = await _renderApiClient.ReportAsync();
                if (reports == null || reports.ResultObj == null)
                {
                    return null;
                }
                ViewBag.Report = reports.ResultObj;

                return View(model);
            }
            return RedirectToAction("Create");
        }

        public async Task<IActionResult> Info(int id)
        {
            var result = await _renderApiClient.GetByIdAsync(id);
            if (result == null || result.ResultObj == null)
            {
                return NotFound();
            }
            return View(result.ResultObj);
        }
        [HttpPost]
        public async Task<IActionResult> Start(int id)
        {
            var result = await _renderApiClient.StartAsync(id);
            if (result == null || !result.IsSuccessed)
            {
                return Json(new { code = ErrorCodeJson.ErrorMess, err = result?.Message ?? "Cập nhật không thành công!" });
            }
            return Json(new { code = ErrorCodeJson.Success });
        }

        [HttpPost]
        public async Task<IActionResult> Stop(int id)
        {
            var result = await _renderApiClient.StopAsync(id);
            if (result == null || !result.IsSuccessed)
            {
                return Json(new { code = ErrorCodeJson.ErrorMess, err = result?.Message ?? "Cập nhật không thành công!" });
            }
            return Json(new { code = ErrorCodeJson.Success });
        }

        [HttpPost]
        public async Task<IActionResult> Delete(int id)
        {
            var result = await _renderApiClient.DeleteAsync(id);
            if (result == null || !result.IsSuccessed)
            {
                return Json(new { code = ErrorCodeJson.ErrorMess, err = result?.Message ?? "Cập nhật không thành công!" });
            }
            return Json(new { code = ErrorCodeJson.Success });
        }

        [HttpGet]
        public async Task<IActionResult> Edit(int id)
        {
            var result = await _renderApiClient.GetByIdAsync(id);
            if (result == null || !result.IsSuccessed)
            {
                return NotFound();
            }
            return View(result.ResultObj);
        }

        [HttpPost]
        public async Task<IActionResult> Edit(int id, RenderUpdateDto model)
        {
            var result = await _renderApiClient.UpdateAsync(id, model);
            if (result == null || !result.IsSuccessed)
            {
                ModelState.AddModelError("", result?.Message ?? "Không thể sửa render!");
                return View(model);
            }
            return RedirectToAction("Create");
        }

        [HttpPost]
        public async Task<IActionResult> ValidateLink(ValidateLinkDto model)
        {
            var result = await _renderApiClient.ValidateLinkAsync(model);
            if (result == null || !result.IsSuccessed)
            {
                return Json(new { code = ErrorCodeJson.ErrorMess, err = result?.Message ?? "Link không hoạt động!" });
            }
            return Json(new { code = ErrorCodeJson.Success });
        }

        [HttpPost]
        public async Task<IActionResult> Clone(int id)
        {
            var result = await _renderApiClient.CloneAsync(id);
            return RedirectToAction("Create");
            //if (result == null || !result.IsSuccessed)
            //{
            //    return Json(new { code = ErrorCodeJson.ErrorMess, err = result?.Message ?? "Cập nhật không thành công!" });
            //}
            //return Json(new { code = ErrorCodeJson.Success });
        }

        [HttpPost]
        [Route("/render/updateData")]
        public IActionResult UpdateData(RenderHistoryDto model, [FromQuery] int index)
        {
            ViewBag.Index = index;
            return PartialView("_UpdateData", model);
        }
    }
}
