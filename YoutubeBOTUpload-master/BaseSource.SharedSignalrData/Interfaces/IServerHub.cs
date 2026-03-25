using BaseSource.SharedSignalrData.Classes;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.SharedSignalrData.Interfaces
{
    public interface IServerHub
    {
        Task PingAsync(PingData pingData);
        Task WorkUpdateAsync(WorkResponse workResponse);
        Task ChromeProfileUpdateAsync(List<ChromeProfileData> chromeProfileDatas);
        Task BotConfigResponseAsync(BotConfig botConfig);
    }
}
