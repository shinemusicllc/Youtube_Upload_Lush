using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UploadYoutubeBot.Interfaces
{
    internal interface IChannelInfo
    {
        string AvatarUrl { get; }
        string ChannelId { get; }
        string ChannelName { get; }
        string Email { get; }
    }
}
