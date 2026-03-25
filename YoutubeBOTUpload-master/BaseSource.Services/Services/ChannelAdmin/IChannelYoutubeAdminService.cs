using BaseSource.ViewModels.ChannelAdmin;
using EFCore.UnitOfWork.PageList;
using BaseSource.SharedSignalrData.Classes;
namespace BaseSource.Services.Services.ChannelAdmin
{
    public interface IChannelYoutubeAdminService
    {
        Task<IPagedList<ChannelAdminDto>> GetAllAsync(ChannelAdminRequestDto model, string userId, bool isAdmin);
        Task<List<ChannelAdminDto>> GetAllByUserIdAsync(string userId, bool isAdmin = false);
        Task<ChannelAdminDto> GetByIdAsync(int id);
        Task<List<ChannelAdminDto>> GetChannelByBotIdAsync(int botId);
        Task<List<UserChannelAdminInfoDto>> GetUserOfChannelIdAsync(int channelId);

        Task<KeyValuePair<bool, string>> UpdateChannelOfUser(UpdateUserChannelDto model);

        Task<KeyValuePair<bool, string>> ChromeProfileUpdateAsync(string botId, List<ChromeProfileData> model);
        Task<KeyValuePair<bool, string>> UpdateProfileAsync(int channelId);
        Task<List<ChannelAdminDto>> GetAllReportAsync();
        Task<KeyValuePair<bool, string>> DeleteAsync(int id);

    }
}
