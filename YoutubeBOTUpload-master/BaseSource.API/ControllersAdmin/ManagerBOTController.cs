using BaseSource.ViewModels.Common;
using BaseSource.Services.Services.BOT;
using BaseSource.ViewModels.ManagerBOT;
using Microsoft.AspNetCore.Mvc;

namespace BaseSource.API.ControllersAdmin
{
    public class ManagerBOTController : BaseAdminApiController
    {
        private readonly IManagerBOTService _managerBOTService;
        public ManagerBOTController(IManagerBOTService managerBOTService)
        {
            _managerBOTService = managerBOTService;
        }

        [HttpPut]
        [Route("/api/admin/bot/{id:int:min(1)}")]
        public async Task<IActionResult> Update([FromRoute] int id, [FromBody] ManagerBotUpdateDto model)
        {
            var result = await _managerBOTService.UpdateBOTAsync(id, model,UserId,IsAdmin);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }

        [HttpDelete]
        [Route("/api/admin/bot/{id:int:min(1)}")]
        public async Task<IActionResult> Delete([FromRoute] int id)
        {
            var result = await _managerBOTService.DeleteAsync(id);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }

        [HttpGet]
        [Route("/api/admin/bots")]
        public async Task<IActionResult> GetAll([FromQuery] ManagerBOTRequestDto model)
        {
            var result = await _managerBOTService.GetBOTByFilterAsync(model, UserId, IsAdmin);
            return Ok(new ApiSuccessResult<object>(result));
        }
        [HttpGet]
        [Route("/api/admin/bot/user")]
        public async Task<IActionResult> GetAllByUser(string userId)
        {
            var result = await _managerBOTService.GetBotByUserIdAsync(userId);
            return Ok(new ApiSuccessResult<object>(result));
        }

        [HttpGet]
        [Route("/api/admin/bot/{id:int:min(1)}/users")]
        public async Task<IActionResult> GetUsersOfBotId(int id)
        {
            var result = await _managerBOTService.GetUserOfBotIdAsync(id);
            return Ok(new ApiSuccessResult<object>(result));
        }

        [HttpGet]
        [Route("/api/admin/bot/{id:int:min(1)}")]
        public async Task<IActionResult> GetById(int id)
        {
            var result = await _managerBOTService.GetByIdAsync(id);
            return Ok(new ApiSuccessResult<object>(result));
        }

        [HttpPost]
        [Route("/api/admin/bot/{id:int:min(1)}/thread")]
        public async Task<IActionResult> UpdateThread([FromBody] BotUpdateThreadDto model)
        {
            var result = await _managerBOTService.UpdateThreadAsync(model, UserId, IsAdmin);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }
    }
}
