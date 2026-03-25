using BaseSource.Shared.Enums;

namespace BaseSource.Data.Entities
{
    public class ManagerBOT
    {
        public int Id { get; set; }
        public string BotId { get; set; }
        public string ConnectionId { get; set; }
        public string Name { get; set; }
        public string Group { get; set; }
        public ManagerBOTStatus Status { get; set; }
        public DateTime CreatedTime { get; set; }
        public DateTime? DeletedTime { get; set; }
        public int Retry { get; set; }
        public int NumberOfThreads { get; set; }
        public double CPU { get; set; }
        public double RAM { get; set; }
        public double Bandwidth { get; set; }
        public double UsageDisk { get; set; }
        public double SpaceDisk { get; set; }
        public DateTime? UpdatedTime { get; set; }
        public LiveType? LiveType { get; set; }
        public bool IsUsed { get; set; }
        public string UserIdManager { get; set; }
        public AppUser User { get; set; }
    

        public ICollection<ChannelYoutube> ChannelYoutubes { get; set; }
    }
}
