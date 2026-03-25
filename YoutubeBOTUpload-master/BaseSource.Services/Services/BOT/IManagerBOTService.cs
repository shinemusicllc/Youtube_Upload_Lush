using BaseSource.Shared.Enums;
using BaseSource.SharedSignalrData.Classes;
using BaseSource.ViewModels.ManagerBOT;
using BaseSource.ViewModels.ManagerBOTAdmin;
using EFCore.UnitOfWork.PageList;

namespace BaseSource.Services.Services.BOT
{
    public interface IManagerBOTService
    {
        Task<KeyValuePair<bool, string>> CreateBOTAsync(ManagerBotCreateDto model);
        Task<KeyValuePair<bool, string>> UpdateBOTAsync(int id, ManagerBotUpdateDto model, string userId, bool isAdmin);
        Task<KeyValuePair<bool, string>> DeleteAsync(int id);
        Task<KeyValuePair<bool, string>> UpdateStatusAsync(int id, ManagerBOTStatus Status);
        Task<IPagedList<ManagerBotInfoDto>> GetBOTByFilterAsync(ManagerBOTRequestDto model, string userId, bool isAdmin = false);
        Task<KeyValuePair<bool, string>> DisconnectBotAsync(string connectionId);
        Task<List<ManagerBotInfoDto>> GetBotByUserIdAsync(string userId);
        Task<List<UserManagerBotAdminInfoDto>> GetUserOfBotIdAsync(int botId);
        Task<ManagerBotInfoDto> GetByIdAsync(int id);

        Task<KeyValuePair<bool, string>> ConnectedAsync(BotConnectedDto model);
        Task<KeyValuePair<bool, string>> DisconnectedAsync(BotConnectedDto model);
        Task<KeyValuePair<bool, string>> UpdateThreadAsync(BotUpdateThreadDto model, string userId, bool isAdmin = false);
        Task<KeyValuePair<bool, string>> UpdateSpaceDiskAsync(string botId, string connectionId, PingData model);

    }
}
