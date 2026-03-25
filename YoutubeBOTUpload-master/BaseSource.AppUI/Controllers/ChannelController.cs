using BaseSource.ApiIntegration.WebApi.Channel;
using Microsoft.AspNetCore.Mvc;

namespace BaseSource.AppUI.Controllers
{
    public class ChannelController : BaseController
    {
        private readonly IChannelApiClient _channelApiClient;
        public ChannelController(
            IChannelApiClient channelApiClient)
        {
            _channelApiClient = channelApiClient;
        }
        public async Task<IActionResult> Index()
        {
            var result = await _channelApiClient.GetChannelByUserAsync();
            if (result == null || result.ResultObj == null)
            {
                return NotFound();
            }
            return View(result.ResultObj);
        }
    }
}
