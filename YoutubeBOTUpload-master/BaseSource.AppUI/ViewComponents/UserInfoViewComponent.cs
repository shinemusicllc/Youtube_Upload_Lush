using BaseSource.ApiIntegration.WebApi;
using BaseSource.ApiIntegration.WebApi.User;
using Microsoft.AspNetCore.Mvc;

namespace BaseSource.AppUI.ViewComponents
{
    public class UserInfoViewComponent : ViewComponent
    {
        private readonly IUserApiClient _userApiClient;
        public UserInfoViewComponent(IUserApiClient userApiClient)
        {
            _userApiClient = userApiClient;
        }
        public async Task<IViewComponentResult> InvokeAsync()
        {
            var userInfo = await _userApiClient.GetUserInfo();
            return View(userInfo.ResultObj);
        }
    }
}
