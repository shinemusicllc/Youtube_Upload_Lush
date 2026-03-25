using BaseSource.ViewModels.Common;
using BaseSource.ViewModels.UserAdmin;

namespace BaseSource.ApiIntegration.WebApi.UserAdmin
{
    public interface IUserAdminApiClient
    {
        Task<ApiResult<PagedResult<UserAdminInfoDto>>> GetUserByFilter(UserAdminRequestDto model);
        Task<ApiResult<string>> UpdateUserGroup(UserGroupAddDto model);
        Task<ApiResult<List<UserGroupDto>>> GetAllUserOfManager(string userId);
        Task<ApiResult<List<UserAdminInfoDto>>> GetAllManager();
        Task<ApiResult<List<UserAdminInfoDto>>> GetAllAdmin();
        Task<ApiResult<string>> UpdateRoleManager(string userName);
        Task<ApiResult<string>> UpdateRoleAdmin(string userName);
        Task<ApiResult<string>> ResetPassword(ResetPasswordAdminDto model);
        //Task<ApiResult<UserManagerBotDto>> GetUserManagerBot(string userId);
        Task<ApiResult<string>> UpdateUserManagerBot(UserManagerBotDto model);
        Task<ApiResult<string>> Delete(string userId);
        Task<ApiResult<string>> Create(UserCreateAdminDto model);
        Task<ApiResult<List<UserManagerBotInfoDto>>> GetUserManagerBot(string userId);
        Task<ApiResult<string>> DeleteUserManagerBot(int id);
        Task<ApiResult<string>> UpdateUserManagetBotAsync(UserManagerBotUpdateDto model);
        Task<ApiResult<string>> InserBOTUser(UserAddBOTAdminDto model);
        Task<ApiResult<string>> UpdateTelegram(UpdateTelegramDto model);
    }
}
