using BaseSource.Shared.Enums;
using BaseSource.SharedSignalrData.Enums;
using System.ComponentModel.DataAnnotations.Schema;

namespace BaseSource.Data.Entities
{
    public class RenderHistory
    {
        public int Id { get; set; }
        public int Order { get; set; }
        public string UserId { get; set; }
        public int ChannelYoutubeId { get; set; }
        public string Intro { get; set; }
        public string VideoLoop { get; set; }
        public string AudioLoop { get; set; }
        public string Outtro { get; set; }
        [NotMapped]
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
        public DateTime? ScheduleTime { get; set; }
        public WorkStatus Status { get; set; }
        //public WorkStatus Action { get; set; }
        public bool IsError { get; set; }
        public double Pencent { get; set; }
        public string ErrorMessage { get; set; }
        public DateTime? DownloadStartTime { get; set; }
        public DateTime? RenderStartTime { get; set; }
        public DateTime? UploadStartTime { get; set; }
        public DateTime? UploadTimeCompleted { get; set; }
        public ChannelYoutube ChannelYoutube { get; set; }
        public AppUser AppUser { get; set; }
    }
}
