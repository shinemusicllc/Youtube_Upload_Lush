using BaseSource.ViewModels.Common;
using BaseSource.Shared.Constants;
using BaseSource.ViewModels.Channel;
using BaseSource.Shared.Extensions;

namespace BaseSource.ApiIntegration.WebApi.Channel
{
    public class ChannelApiClient : IChannelApiClient
    {
        private readonly IHttpClientFactory _httpClientFactory;

        public ChannelApiClient(IHttpClientFactory httpClientFactory)
        {
            _httpClientFactory = httpClientFactory;
        }
        public async Task<ApiResult<List<ChannelYoutubeDto>>> GetChannelByUserAsync()
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<List<ChannelYoutubeDto>>>($"/api/channels");
        }
    }
}
