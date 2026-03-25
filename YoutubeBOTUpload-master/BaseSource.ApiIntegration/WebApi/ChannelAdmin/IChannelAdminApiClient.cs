using BaseSource.ViewModels.Common;
using BaseSource.ViewModels.ChannelAdmin;

namespace BaseSource.ApiIntegration.WebApi.ChannelAdmin
{
    public interface IChannelAdminApiClient
    {
        Task<ApiResult<PagedResult<ChannelAdminDto>>> GetAllAsync(ChannelAdminRequestDto model);
        Task<ApiResult<List<ChannelAdminDto>>> GetAllByUserIdAsync(string userId);
        Task<ApiResult<ChannelAdminDto>> GetByIdAsync(int id);
        Task<ApiResult<List<ChannelAdminDto>>> GetChannelByBotIdAsync(int botId);
        Task<ApiResult<List<UserChannelAdminInfoDto>>> GetUserOfChannelIdAsync(int channelId);
        Task<ApiResult<string>> UpdateChannelOfUser(UpdateUserChannelDto model);
        Task<ApiResult<List<ChannelAdminDto>>> GetAllReportAsync();
        Task<ApiResult<string>> UpdateProfileAsync(int id);
        Task<ApiResult<string>> DeleteAsync(int id);
    }
}
