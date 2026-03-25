using BaseSource.ViewModels.Common;
using BaseSource.ViewModels.Render;
using BaseSource.ViewModels.RenderAdmin;

namespace BaseSource.ApiIntegration.WebApi.RenderAdmin
{
    public interface IRenderAdminApiClient
    {
        Task<ApiResult<PagedResult<RenderAdminInfoDto>>> GetAllAsync(RenderAdminRequestDto model);
        Task<ApiResult<RenderHistoryDto>> GetByIdAsync(int id);
        Task<ApiResult<List<RenderAdminInfoDto>>> GetAllByChannelAsync(int channelId);
        Task<ApiResult<string>> DeleteAllAsync();
        
    }
}
