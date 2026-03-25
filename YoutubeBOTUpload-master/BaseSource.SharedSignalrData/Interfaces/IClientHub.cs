using BaseSource.SharedSignalrData.Classes;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace BaseSource.SharedSignalrData.Interfaces
{
    public interface IClientHub
    {
        Task PushWorkAsync(WorkData workData);
        Task CancelWorkAsync(Identy identy);
        Task GetInfoChannelAsync(string profileId);
        Task ChangeBotConfigAsync(BotConfig botConfig);
        Task DeleteProfilesAsync(IReadOnlyList<string> profileIds);
    }
}
