namespace BaseSource.Data.Entities
{
    public class UserChannel
    {
        public int Id { get; set; }
        public int ChannelYoutubeId { get; set; }
        public string UserId { get; set; }
        public byte Status { get; set; }
        public DateTime CreatedTime { get; set; }


        public virtual AppUser AppUser { get; set; }

        public virtual ChannelYoutube ChannelYoutube { get; set; }
    }
}
