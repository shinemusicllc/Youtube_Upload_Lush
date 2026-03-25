using BaseSource.ViewModels.Common;
using BaseSource.ViewModels.Render;
using BaseSource.ViewModels.RenderAdmin;
using BaseSource.Shared.Extensions;
using BaseSource.Shared.Constants;
using BaseSource.ViewModels.Report;

namespace BaseSource.ApiIntegration.WebApi.Render
{
    public class RenderApiClient : IRenderApiClient
    {
        private readonly IHttpClientFactory _httpClientFactory;

        public RenderApiClient(IHttpClientFactory httpClientFactory)
        {
            _httpClientFactory = httpClientFactory;
        }
        public async Task<ApiResult<string>> CloneAsync(int id)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PatchAsync<ApiResult<string>>($"/api/renderHistory/{id}/clone");
        }

        public async Task<ApiResult<string>> CreateAsync(RenderCreateDto model)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PostAsync<ApiResult<string>>($"/api/renderHistory", model);
        }

        public async Task<ApiResult<string>> DeleteAsync(int id)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.DeleteAsync<ApiResult<string>>($"/api/renderHistory/{id}");
        }

        public async Task<ApiResult<PagedResult<RenderHistoryDto>>> GetAllAsync(RenderRequestDto model)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<PagedResult<RenderHistoryDto>>>($"/api/renderHistorys", model);
        }

        public async Task<ApiResult<RenderHistoryDto>> GetByIdAsync(int id)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<RenderHistoryDto>>($"/api/renderHistory/{id}");
        }

        public async Task<ApiResult<RenderReportClientDto>> ReportAsync()
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<RenderReportClientDto>>($"/api/renderHistory/report");
        }

        public async Task<ApiResult<string>> StartAsync(int id)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PatchAsync<ApiResult<string>>($"/api/renderHistory/{id}/start");
        }

        public async Task<ApiResult<string>> StopAsync(int id)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PatchAsync<ApiResult<string>>($"/api/renderHistory/{id}/stop");
        }

        public async Task<ApiResult<string>> UpdateAsync(int id, RenderUpdateDto model)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PutAsync<ApiResult<string>>($"/api/renderHistory/{id}", model);
        }

        public async Task<ApiResult<string>> ValidateLinkAsync(ValidateLinkDto model)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PostAsync<ApiResult<string>>($"/api/renderHistory/validateLink", model);
        }
    }
}
