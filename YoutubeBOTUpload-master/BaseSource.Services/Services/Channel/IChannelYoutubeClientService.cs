using BaseSource.ViewModels.Channel;

namespace BaseSource.Services.Services.Channel
{
    public interface IChannelYoutubeClientService
    {
        Task<List<ChannelYoutubeDto>> GetChannelByUser(string userId);
        Task<KeyValuePair<bool,string>> AddChannelToUserAsync(AddUserChannelDto model);
    }
}
