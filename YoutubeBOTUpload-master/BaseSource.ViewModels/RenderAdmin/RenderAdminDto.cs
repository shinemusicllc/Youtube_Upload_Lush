using BaseSource.Shared.Enums;
using BaseSource.SharedSignalrData.Enums;
using BaseSource.ViewModels.Common;

namespace BaseSource.ViewModels.RenderAdmin
{
    public class RenderAdminInfoDto
    {
        public int Id { get; set; }
        public int Order { get; set; }
        public string UserId { get; set; }
        public string UserName { get; set; }
        public int ChannelId { get; set; }
        public string ChannelYTId { get; set; }
        public string ChannelName { get; set; }
        public string Intro { get; set; }
        public string VideoLoop { get; set; }
        public string AudioLoop { get; set; }
        public string Outtro { get; set; }
        public TimeSpan TimeRender
        {
            get
            {
                return new TimeSpan(TimeRenderLong);
            }
        }
        public long TimeRenderLong { get; set; }
        public string VideoName { get; set; }
        public string VideoLink { get; set; }
        public DateTime CreatedTime { get; set; }
        public DateTime? DeletedTime { get; set; }
        public DateTime? UpdatedTime { get; set; }
        public WorkStatus Status { get; set; }
        public bool IsError { get; set; }
        public double Pencent { get; set; }
        public string ErrorMessage { get; set; }
        public string BotName { get; set; }
        public DateTime? DownloadStartTime { get; set; }
        public DateTime? RenderStartTime { get; set; }
        public DateTime? UploadStartTime { get; set; }
        public DateTime? UploadTimeCompleted { get; set; }
        public DateTime? ScheduleTime { get; set; }
        public string Group { get; set; }
        public string Gmail { get; set; }
        public string Avatar { get; set; }
        public string UserIdManager { get; set; }
        public string UserManager { get; set; }
    }

    public class RenderAdminRequestDto : PageQuery
    {
        public string Managers { get; set; }

    }
    public class ValidateLinkDto
    {
        public string Link { get; set; }
    }
}
