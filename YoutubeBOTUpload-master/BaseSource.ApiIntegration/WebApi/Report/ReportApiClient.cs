using BaseSource.ViewModels.Common;
using BaseSource.ViewModels.Report;
using BaseSource.Shared.Extensions;
using BaseSource.Shared.Constants;

namespace BaseSource.ApiIntegration.WebApi.Report
{
    public class ReportApiClient : IReportApiClient
    {
        private readonly IHttpClientFactory _httpClientFactory;

        public ReportApiClient(IHttpClientFactory httpClientFactory)
        {
            _httpClientFactory = httpClientFactory;
        }
        public async Task<ApiResult<ReportDto>> GeReportAsync(string managers)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<ReportDto>>($"/api/admin/report?managers={managers}");
        }
    }
}
