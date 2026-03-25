using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UploadYoutubeBot.DataClass
{
    internal class SettingData
    {
        public int ThreadCount { get; set; } = 1;
        public int ChromeVer { get; set; } = 0;
        public Guid BotId { get; set; } = Guid.NewGuid();
        public string ApiDomain { get; set; } = "https://apiytb.shinemusicllc.com/";
    }
}
