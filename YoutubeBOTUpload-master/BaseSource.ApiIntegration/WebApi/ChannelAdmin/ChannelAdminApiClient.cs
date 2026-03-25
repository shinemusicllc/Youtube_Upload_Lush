using BaseSource.ViewModels.Common;
using BaseSource.ViewModels.ChannelAdmin;
using BaseSource.Shared.Extensions;
using BaseSource.Shared.Constants;

namespace BaseSource.ApiIntegration.WebApi.ChannelAdmin
{
    public class ChannelAdminApiClient : IChannelAdminApiClient
    {
        private readonly IHttpClientFactory _httpClientFactory;

        public ChannelAdminApiClient(IHttpClientFactory httpClientFactory)
        {
            _httpClientFactory = httpClientFactory;
        }
        public async Task<ApiResult<PagedResult<ChannelAdminDto>>> GetAllAsync(ChannelAdminRequestDto model)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<PagedResult<ChannelAdminDto>>>("/api/admin/channels", model);
        }

        public async Task<ApiResult<ChannelAdminDto>> GetByIdAsync(int id)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<ChannelAdminDto>>($"/api/admin/channel/{id}");
        }

        public async Task<ApiResult<List<ChannelAdminDto>>> GetAllByUserIdAsync(string userId)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<List<ChannelAdminDto>>>($"/api/admin/channels/user?userId={userId}");
        }

        public async Task<ApiResult<List<ChannelAdminDto>>> GetChannelByBotIdAsync(int botId)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<List<ChannelAdminDto>>>($"/api/admin/channel/bot/{botId}");
        }

        public async Task<ApiResult<List<UserChannelAdminInfoDto>>> GetUserOfChannelIdAsync(int channelId)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<List<UserChannelAdminInfoDto>>>($"/api/admin/channel/{channelId}/users");
        }

        public async Task<ApiResult<string>> UpdateChannelOfUser(UpdateUserChannelDto model)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PostAsync<ApiResult<string>>($"/api/admin/channel/update-user", model);
        }

        public async Task<ApiResult<List<ChannelAdminDto>>> GetAllReportAsync()
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<List<ChannelAdminDto>>>($"/api/admin/chanel/report");
        }

        public async Task<ApiResult<string>> UpdateProfileAsync(int id)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PostAsync<ApiResult<string>>($"/api/admin/chanel/{id}/profile");
        }

        public async Task<ApiResult<string>> DeleteAsync(int id)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PostAsync<ApiResult<string>>($"/api/admin/channel/delete/{id}");
        }
    }
}
