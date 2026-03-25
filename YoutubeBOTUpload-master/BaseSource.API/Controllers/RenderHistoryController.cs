using BaseSource.ViewModels.Common;
using BaseSource.Services.Services.Render;
using BaseSource.ViewModels.Render;
using BaseSource.ViewModels.RenderAdmin;
using Microsoft.AspNetCore.Mvc;

namespace BaseSource.API.Controllers
{
    public class RenderHistoryController : BaseApiController
    {
        private readonly IRenderClientService _renderClientService;
        public RenderHistoryController(IRenderClientService renderClientService)
        {
            _renderClientService = renderClientService;
        }

        [HttpPost]
        public async Task<IActionResult> Create([FromBody] RenderCreateDto model)
        {
            var result = await _renderClientService.CreateAsync(UserId, model);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }

        [HttpPut]
        [Route("{id:int:min(1)}")]
        public async Task<IActionResult> Update(int id,[FromBody] RenderUpdateDto model)
        {
            var result = await _renderClientService.UpdateAsync(UserId, id, model);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }

        [HttpPatch]
        [Route("{id:int:min(1)}/start")]
        public async Task<IActionResult> Start(int id)
        {
            var result = await _renderClientService.StartAsync(UserId, id);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }

        [HttpPatch]
        [Route("{id:int:min(1)}/stop")]
        public async Task<IActionResult> Stop(int id)
        {
            var result = await _renderClientService.StopAsync(UserId, id);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }

        [HttpDelete]
        [Route("{id:int:min(1)}")]
        public async Task<IActionResult> Delete(int id)
        {
            var result = await _renderClientService.DeleteAsync(UserId, id);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }

        [HttpPatch]
        [Route("{id:int:min(1)}/clone")]
        public async Task<IActionResult> Clone(int id)
        {
            var result = await _renderClientService.CloneAsync(UserId, id);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }

        [HttpPost]
        [Route("validateLink")]
        public async Task<IActionResult> ValidateLink([FromBody] ValidateLinkDto model)
        {
            var result = await _renderClientService.ValidateLinkAsync(model.Link);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }

        [HttpGet]
        [Route("{id:int:min(1)}")]
        public async Task<IActionResult> GetById(int id)
        {
            var result = await _renderClientService.GetRenderByIdAsync(UserId, id);
            return Ok(new ApiSuccessResult<object>(result));
        }

        [HttpGet]
        [Route("/api/renderhistorys")]
        public async Task<IActionResult> GetAll([FromQuery] RenderRequestDto model)
        {
            var result = await _renderClientService.GetByFilterAsync(UserId, model);
            return Ok(new ApiSuccessResult<object>(result));
        }

        [HttpGet]
        [Route("report")]
        public async Task<IActionResult> Report()
        {
            var result = await _renderClientService.GetReportRenderAsync(UserId);
            return Ok(new ApiSuccessResult<object>(result));
        }
    }
}
