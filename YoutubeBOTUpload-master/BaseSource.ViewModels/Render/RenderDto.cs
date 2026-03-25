using BaseSource.Shared.Enums;
using BaseSource.SharedSignalrData.Enums;
using BaseSource.ViewModels.Common;
using System.ComponentModel.DataAnnotations;

namespace BaseSource.ViewModels.Render
{
    public class RenderHistoryDto
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
        public TimeSpan TimeRender { get; set; }
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
        public string Group { get; set; }
        public DateTime? ScheduleTime { get; set; }
        public DateTime? DownloadStartTime { get; set; }
        public DateTime? RenderStartTime { get; set; }
        public DateTime? UploadStartTime { get; set; }
        public DateTime? UploadTimeCompleted { get; set; }
        public string Avatar { get; set; }
    }
    public class RenderCreateDto
    {
        public int ChannelId { get; set; }
        public string Intro { get; set; }
        public string VideoLoop { get; set; }
        public string AudioLoop { get; set; }
        public string Outtro { get; set; }

        public TimeSpan TimeRender { get; set; }
        public string TimeRenderString { get; set; }
        public DateTime? ScheduleTime { get; set; }
        [MaxLength(100,ErrorMessage ="Tên video phải nhỏ hơn 100 ký và không chứa ký tự đặc biệt ,không sử dụng dấu, icon")]
        [RegularExpression(@"^[^<>,?;:'()!~%\@#/*""]+$",ErrorMessage ="Tên video phải nhỏ hơn 100 ký và không chứa ký tự đặc biệt ,không sử dụng dấu, icon")]
        public string VideoName { get; set; }
    }

    public class RenderUpdateDto
    {
        public int Id { get; set; }
        public int Order { get; set; }
        public string UserId { get; set; }
        public int ChannelId { get; set; }
        public string Intro { get; set; }
        public string VideoLoop { get; set; }
        public string AudioLoop { get; set; }
        public string Outtro { get; set; }
        public TimeSpan TimeRender { get; set; }
        public string VideoName { get; set; }
        public DateTime CreatedTime { get; set; }
        public RenderStatus Status { get; set; }
        public RenderAction Action { get; set; }
    }

    public class RenderRequestDto : PageQuery
    {

    }
}
