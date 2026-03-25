using BaseSource.ViewModels.Common;
using BaseSource.Services.Services.RenderAdmin;
using BaseSource.ViewModels.RenderAdmin;
using Microsoft.AspNetCore.Mvc;

namespace BaseSource.API.ControllersAdmin
{
    public class RenderHistoryController : BaseAdminApiController
    {
        private readonly IRenderAdminService _renderAdminService;
        public RenderHistoryController(IRenderAdminService renderAdminService)
        {
            _renderAdminService = renderAdminService;
        }

        [HttpGet]
        [Route("/api/admin/renders")]
        public async Task<IActionResult> GetAll([FromQuery] RenderAdminRequestDto model)
        {
            var result = await _renderAdminService.GetAllAsync(model, UserId, IsAdmin);
            return Ok(new ApiSuccessResult<object>(result));
        }
        [HttpGet]
        [Route("/api/admin/renders/{id:int:min(1)}")]
        public async Task<IActionResult> GetAllByChannel(int id)
        {
            var result = await _renderAdminService.GetAllByChannelAsync(id);
            return Ok(new ApiSuccessResult<object>(result));
        }
        [HttpGet]
        [Route("/api/admin/render/{id:int:min(1)}")]
        public async Task<IActionResult> GetById(int id)
        {
            var result = await _renderAdminService.GetByIdAsync(id);
            return Ok(new ApiSuccessResult<object>(result));
        }

        [HttpDelete]
        [Route("/api/admin/renders")]
        public async Task<IActionResult> Delete()
        {
            var result = await _renderAdminService.DeleteAsync(UserName);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }
    }
}
