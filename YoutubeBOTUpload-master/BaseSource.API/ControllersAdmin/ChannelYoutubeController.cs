using BaseSource.ViewModels.Common;
using BaseSource.Services.Services.ChannelAdmin;
using BaseSource.ViewModels.ChannelAdmin;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;

namespace BaseSource.API.ControllersAdmin
{
    public class ChannelYoutubeController : BaseAdminApiController
    {
        private readonly IChannelYoutubeAdminService _channelYoutubeAdminService;
        public ChannelYoutubeController(IChannelYoutubeAdminService channelYoutubeAdminService)
        {
            _channelYoutubeAdminService = channelYoutubeAdminService;
        }

        [HttpGet]
        [Route("/api/admin/channels")]
        public async Task<IActionResult> GetAll([FromQuery] ChannelAdminRequestDto model)
        {
            var result = await _channelYoutubeAdminService.GetAllAsync(model, UserId, IsAdmin);
            return Ok(new ApiSuccessResult<object>(result));
        }

        [HttpGet]
        [Route("/api/admin/channels/user")]
        public async Task<IActionResult> GetAllByUserId(string userId)
        {
            var result = await _channelYoutubeAdminService.GetAllByUserIdAsync(userId, IsAdmin);
            return Ok(new ApiSuccessResult<object>(result));
        }

        [HttpGet]
        [Route("/api/admin/channel/{id:int:min(1)}")]
        public async Task<IActionResult> GetById(int id)
        {
            var result = await _channelYoutubeAdminService.GetByIdAsync(id);
            return Ok(new ApiSuccessResult<object>(result));
        }

        [HttpGet]
        [Route("/api/admin/channel/bot/{id:int:min(1)}")]
        public async Task<IActionResult> GetChannelByBotId(int id)
        {
            var result = await _channelYoutubeAdminService.GetChannelByBotIdAsync(id);
            return Ok(new ApiSuccessResult<object>(result));
        }
        [HttpGet]
        [Route("/api/admin/channel/{id:int:min(1)}/users")]
        public async Task<IActionResult> GetUserByChannelId(int id)
        {
            var result = await _channelYoutubeAdminService.GetUserOfChannelIdAsync(id);
            return Ok(new ApiSuccessResult<object>(result));
        }

        [HttpPost]
        [Route("/api/admin/channel/update-user")]
        public async Task<IActionResult> UpdateUserChannel([FromBody] UpdateUserChannelDto model)
        {
            var result = await _channelYoutubeAdminService.UpdateChannelOfUser(model);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }

        [HttpGet]
        [Route("/api/admin/chanel/report")]
        public async Task<IActionResult> GetAllReport()
        {
            var result = await _channelYoutubeAdminService.GetAllReportAsync();
            return Ok(new ApiSuccessResult<object>(result));
        }

        [HttpPost]
        [AllowAnonymous]
        [Route("/api/admin/chanel/{id:int:min(1)}/profile")]
        public async Task<IActionResult> UpdateProfile(int id)
        {
            var result = await _channelYoutubeAdminService.UpdateProfileAsync(id);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }

        [HttpPost]
        [AllowAnonymous]
        [Route("/api/admin/channel/delete/{id:int:min(1)}")]
        public async Task<IActionResult> Delete(int id)
        {
            var result = await _channelYoutubeAdminService.DeleteAsync(id);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }
    }
}
