using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UploadYoutubeBot.DataClass
{
    internal class ProfileData
    {
        public string ProfileId { get; set; } = Guid.NewGuid().ToString();
        public string Email { get; set; }
        public string ChannelId { get; set; }
        public string ChannelName { get; set; }
        public string AvatarUrl { get; set; }
        public string GroupName { get; set; }
    }
}
