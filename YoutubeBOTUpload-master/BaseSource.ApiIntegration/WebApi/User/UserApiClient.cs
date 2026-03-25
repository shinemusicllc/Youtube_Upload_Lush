using BaseSource.ViewModels.Common;
using BaseSource.ViewModels.User;
using BaseSource.Shared.Constants;
using BaseSource.Shared.Extensions;

namespace BaseSource.ApiIntegration.WebApi.User
{
    public class UserApiClient : IUserApiClient
    {
        private readonly IHttpClientFactory _httpClientFactory;

        public UserApiClient(IHttpClientFactory httpClientFactory)
        {
            _httpClientFactory = httpClientFactory;
        }
        public async Task<ApiResult<string>> Authenticate(LoginRequestVm model)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            var result = await client.PostAsync<ApiResult<string>>("/api/Account/Authenticate", model);
            return result;
        }

        public async Task<ApiResult<string>> ChangePassword(ChangePasswordVm model)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PostAsync<ApiResult<string>>("/api/Account/ChangePassword", model);
        }

        public async Task<ApiResult<string>> ConfirmEmail(ConfirmEmailVm model)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PostAsync<ApiResult<string>>("/api/Account/ConfirmEmail", model);
        }

        public async Task<ApiResult<string>> ForgotPassword(ForgotPasswordVm model)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PostAsync<ApiResult<string>>("/api/Account/ForgotPassword", model);
        }

        public async Task<ApiResult<PackageLiveUserDto>> GetPackageInfo()
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<PackageLiveUserDto>>("/api/Account/packageInfo");
        }

        public async Task<ApiResult<ProfifleInfoDto>> GetProfileInfo()
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<ProfifleInfoDto>>("/api/Account/profile");
        }

        public async Task<ApiResult<UserInfoResponse>> GetUserInfo()
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.GetAsync<ApiResult<UserInfoResponse>>("/api/Account/GetUserInfo");
        }

        public async Task<ApiResult<string>> Register(RegisterRequestVm model)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PostAsync<ApiResult<string>>("/api/Account/Register", model);
        }

        public async Task<ApiResult<string>> ResetPassword(ResetPasswordVm model)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PostAsync<ApiResult<string>>("/api/Account/ResetPassword", model);
        }

        public async Task<ApiResult<string>> Update(UserUpdateDto model)
        {
            var client = _httpClientFactory.CreateClient(SystemConstants.BackendApiClient);
            return await client.PostAsync<ApiResult<string>>("/api/Account/Update", model);
        }
    }
}
