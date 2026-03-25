using BaseSource.ViewModels.Common;
using BaseSource.ViewModels.Channel;

namespace BaseSource.ApiIntegration.WebApi.Channel
{
    public interface IChannelApiClient
    {
        Task<ApiResult<List<ChannelYoutubeDto>>> GetChannelByUserAsync();
    }
}
