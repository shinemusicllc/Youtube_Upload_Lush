using BaseSource.ViewModels.Common;
using BaseSource.ViewModels.ManagerBOT;
using BaseSource.ViewModels.ManagerBOTAdmin;

namespace BaseSource.ApiIntegration.WebApi.ManagerBOT
{
    public interface IManagerBOTApiClient
    {
        Task<ApiResult<string>> CreateBOTAsync(ManagerBotCreateDto model);
        Task<ApiResult<PagedResult<ManagerBotInfoDto>>> GetBOTByFilterAsync(ManagerBOTRequestDto model);
        Task<ApiResult<int>> GetTotalBOTInRunAsync();
        Task<ApiResult<string>> UpdateBOTAsync(int id, ManagerBotUpdateDto model);
        Task<ApiResult<string>> DeleteAsync(int id);
        Task<ApiResult<string>> ChangeUsedAsync(int id);
        Task<ApiResult<ManagerBotInfoDto>> GetById(int id);
        Task<ApiResult<List<ManagerBotInfoDto>>> GetBotByUserIdAsync(string userId);
        Task<ApiResult<List<UserManagerBotAdminInfoDto>>> GetUserOfBotIdAsync(int botId);
        Task<ApiResult<string>> UpdateThreadAsync(BotUpdateThreadDto model);
    }
}
