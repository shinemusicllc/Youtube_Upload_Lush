using BaseSource.Shared.Enums;
using BaseSource.ViewModels.Common;
using System.Diagnostics;

namespace BaseSource.ViewModels.ChannelAdmin
{
    public class ChannelAdminDto
    {
        public int Id { get; set; }
        public string Avatar { get; set; }
        public string ChannelName { get; set; }
        public string ChannelYTId { get; set; }
        public string ChannelLink { get; set; }
        public string BotName { get; set; }
        public string ChannelGmail { get; set; }
        public string Group { get; set; }
        public DateTime CreatedTime { get; set; }
        public int TotalUser { get; set; }
        public ManagerBOTStatus Status { get; set; }
        public bool IsUsed { get; set; }
        public string UserIdManager { get; set; }
        public string UserManager { get; set; }
        public List<string> UserJoins { get; set; }
    }
    public class ChannelAdminRequestDto : PageQuery
    {
        public string Managers { get; set; }
    }
    public class UserChannelAdminInfoDto
    {
        public string UserId { get; set; }
        public string UserName { get; set; }
        public string Password { get; set; }
        public int TotalChannel { get; set; }
        public int TotalBot { get; set; }
    }

    public class UpdateUserChannelDto
    {
        public string UserId { get; set; }
        public string UserName { get; set; }
        public int ChannelId { get; set; }
    }
}
