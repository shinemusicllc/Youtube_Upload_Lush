namespace BaseSource.Data.Entities
{
    public class ChannelYoutube
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Avatar { get; set; }
        public string ChannelYTId { get; set; }
        public int ManagerBOTId { get; set; }
        public string Cookie { get; set; }
        public string Gmail { get; set; }
        public string ProfileId { get; set; }
        public DateTime? UpdatedTime { get; set; }
        public DateTime CreatedTime { get; set; }
        public DateTime? DeletedTime { get; set; }
        public ManagerBOT ManagerBOT { get; set; }

        public ICollection<RenderHistory> RenderHistorys { get; set; }
        public ICollection<UserChannel> UserChannels { get; set; }
    }
}
