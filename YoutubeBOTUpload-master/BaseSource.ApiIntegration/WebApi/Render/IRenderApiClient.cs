using BaseSource.ViewModels.Common;
using BaseSource.ViewModels.Render;
using BaseSource.ViewModels.RenderAdmin;
using BaseSource.ViewModels.Report;

namespace BaseSource.ApiIntegration.WebApi.Render
{
    public interface IRenderApiClient
    {
        Task<ApiResult<string>> CreateAsync(RenderCreateDto model);
        Task<ApiResult<string>> UpdateAsync(int id, RenderUpdateDto model);
        Task<ApiResult<string>> StartAsync(int id);
        Task<ApiResult<string>> StopAsync(int id);
        Task<ApiResult<string>> DeleteAsync(int id);
        Task<ApiResult<string>> CloneAsync(int id);
        Task<ApiResult<string>> ValidateLinkAsync(ValidateLinkDto model);
        Task<ApiResult<RenderHistoryDto>> GetByIdAsync(int id);
        Task<ApiResult<PagedResult<RenderHistoryDto>>> GetAllAsync(RenderRequestDto model);
        Task<ApiResult<RenderReportClientDto>> ReportAsync();
    }
}
