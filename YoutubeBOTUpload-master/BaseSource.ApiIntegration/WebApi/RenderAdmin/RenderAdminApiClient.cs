using BaseSource.ViewModels.Common;
using BaseSource.ViewModels.RenderAdmin;
using BaseSource.Shared.Constants;
using BaseSource.Shared.Extensions;
using BaseSource.ViewModels.Render;

namespace BaseSource.ApiIntegration.WebApi.RenderAdmin
{
    public class RenderAdminApiClient : IRenderAdminApiClient
    {
        private readonly IHttpClientFactory _httpClientFactory;

        public RenderAdminApiClient(IHttpClientFactory httpClientFactory)
        {
            _httpClientFactory = httpClientFactory;
        }

        public async Task<ApiResult<string>> DeleteAllAsync()
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.DeleteAsync<ApiResult<string>>($"/api/admin/renders");
        }

        public async Task<ApiResult<PagedResult<RenderAdminInfoDto>>> GetAllAsync(RenderAdminRequestDto model)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<PagedResult<RenderAdminInfoDto>>>($"/api/admin/renders",model);
        }

        public async Task<ApiResult<List<RenderAdminInfoDto>>> GetAllByChannelAsync(int channelId)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<List<RenderAdminInfoDto>>>($"/api/admin/renders/{channelId}");
        }

        public async Task<ApiResult<RenderHistoryDto>> GetByIdAsync(int id)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<RenderHistoryDto>>($"/api/admin/render/{id}");
        }
    }
}
