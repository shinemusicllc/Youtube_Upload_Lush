namespace BaseSource.Data.Entities
{
    public class ConfigSystem
    {
        public int Id { get; set; }
        public string BankNumber { get; set; }
        public string BankName { get; set; }
        public string BankAccountName { get; set; }
        public string LinkFBAdmin { get; set; }
        public string LinkYoutube { get; set; }
        public string UserDeleteChannel { get; set; }
        public DateTime? DeletedTimeChannel { get; set; }
    }
}
