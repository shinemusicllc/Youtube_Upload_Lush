using BaseSource.ViewModels.Common;
using BaseSource.Services.Services.Channel;
using Microsoft.AspNetCore.Mvc;

namespace BaseSource.API.Controllers
{
    public class ChannelYoutubeController : BaseApiController
    {
        private readonly IChannelYoutubeClientService _channelYoutubeClientService;
        public ChannelYoutubeController(IChannelYoutubeClientService channelYoutubeClientService)
        {
            _channelYoutubeClientService = channelYoutubeClientService;
        }
        [HttpGet]
        [Route("/api/channels")]
        public async Task<IActionResult> GetChannelByUser()
        {
            var result =await _channelYoutubeClientService.GetChannelByUser(UserId);
            return Ok(new ApiSuccessResult<object>(result));
        }
    }
}
