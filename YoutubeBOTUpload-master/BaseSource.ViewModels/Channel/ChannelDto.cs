using BaseSource.Shared.Enums;

namespace BaseSource.ViewModels.Channel
{
    public class ChannelYoutubeDto
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Avatar { get; set; }
        public string ChannelYTId { get; set; }
        public int ManagerBOTId { get; set; }
        public string Cookie { get; set; }
        public string BotName { get; set; }
        public string BotGroup { get; set; }
        public ManagerBOTStatus Status { get; set; }
    }
    public class AddUserChannelDto
    {
        public int ChannelYoutubeId { get; set; }
        public string UserId { get; set; }
    }
}
