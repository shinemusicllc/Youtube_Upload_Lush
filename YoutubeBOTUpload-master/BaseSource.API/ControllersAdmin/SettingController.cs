using BaseSource.ViewModels.Common;
using BaseSource.Services.Services.Setting;
using BaseSource.ViewModels.Setting;
using Microsoft.AspNetCore.Mvc;

namespace BaseSource.API.ControllersAdmin
{
    [Route("api/admin/[controller]")]
    public class SettingController : BaseAdminApiController
    {
        private readonly IConfigSettingService _configSettingService;
        public SettingController(IConfigSettingService configSettingService)
        {
            _configSettingService = configSettingService;
        }


        [HttpGet]
        [Route("/api/admin/setting")]
        public async Task<IActionResult> GetSetting()
        {
            var result = await _configSettingService.GetSettingAsync();
            return Ok(new ApiSuccessResult<object>(result));
        }
        [HttpPost]
        public async Task<IActionResult> Update([FromBody] ConfigSettingVm model)
        {
            var result = await _configSettingService.UpdateAsync(model);

            if (result.Key)
                return Ok(new ApiSuccessResult<string>(string.Empty));

            // AddErrors(result.Value, string.Empty);
            return BadRequest(new ApiErrorResult<string>(result.Value));
        }
    }
}
