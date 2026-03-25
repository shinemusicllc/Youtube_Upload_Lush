using BaseSource.ViewModels.Common;
using BaseSource.ViewModels.Report;

namespace BaseSource.ApiIntegration.WebApi.Report
{
    public interface IReportApiClient
    {
        Task<ApiResult<ReportDto>> GeReportAsync(string managers);
    }
}
