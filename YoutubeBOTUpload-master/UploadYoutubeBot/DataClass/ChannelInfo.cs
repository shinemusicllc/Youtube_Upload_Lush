using UploadYoutubeBot.Interfaces;

namespace UploadYoutubeBot.DataClass
{
    class ChannelInfo : IChannelInfo
    {
        public string ChannelName { get; set; }
        public string Email { get; set; }
        public string ChannelId { get; set; }
        public string AvatarUrl { get; set; }
    }
}
