using BaseSource.ViewModels.UserAdmin;
using EFCore.UnitOfWork.PageList;

namespace BaseSource.Services.Services.UserAdmin
{
    public interface IUserAdminService
    {
        Task<IPagedList<UserAdminInfoDto>> GetUserByFilterAsync(UserAdminRequestDto model, string userId, bool isAdmin);
        Task<KeyValuePair<bool, string>> UpdateManagerAsync(string userName);
        Task<KeyValuePair<bool, string>> UpdateAdminAsync(string userName);
        Task<List<UserAdminInfoDto>> GetUserManagerAsync();
        Task<List<UserAdminInfoDto>> GetUserAdminAsync();
        Task<List<UserGroupDto>> GetAllUserOfManagerAsync(string userId);
        Task<KeyValuePair<bool, string>> ResetPassowrdAsync(ResetPasswordAdminDto model);
        Task<UserManagerBotDto> GetUserManagerBotAsync(string userId);
        Task<KeyValuePair<bool, string>> DeleteAsync(string userId);
        Task<KeyValuePair<bool, string>> CreateUserAsync(UserCreateAdminDto model);

        Task<List<UserManagerBotInfoDto>> GetUserBotAsync(string userId);

        Task<KeyValuePair<bool, string>> InsertBOTOfUserAsync(UserAddBOTAdminDto model);
        Task<KeyValuePair<bool, string>> UpdateTelegramUserAsync(UpdateTelegramDto model, string userId, bool isAdmin);
        //Task<>

    }
}
