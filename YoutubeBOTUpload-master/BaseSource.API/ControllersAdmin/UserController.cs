using BaseSource.Services.Services.UserAdmin;
using BaseSource.ViewModels.Common;
using BaseSource.ViewModels.UserAdmin;
using Microsoft.AspNetCore.Mvc;

namespace BaseSource.API.ControllersAdmin
{
    [Route("/api/admin/[controller]")]
    public class UserController : BaseAdminApiController
    {
        private readonly IUserAdminService _userAdminService;
        public UserController(IUserAdminService userAdminService)
        {
            _userAdminService = userAdminService;
        }

        [HttpGet]
        [Route("/api/admin/users")]
        public async Task<IActionResult> GetAll([FromQuery] UserAdminRequestDto model)
        {
            var result = await _userAdminService.GetUserByFilterAsync(model, UserId, IsAdmin);
            return Ok(new ApiSuccessResult<object>(result));
        }



        [HttpPost]
        [Route("telegram")]
        public async Task<IActionResult> UpdateTelegam(UpdateTelegramDto model)
        {
            var result = await _userAdminService.UpdateTelegramUserAsync(model, UserId, IsAdmin);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }

        [HttpGet]
        [Route("managers")]
        public async Task<IActionResult> GetAllManager()
        {
            var result = await _userAdminService.GetUserManagerAsync();
            return Ok(new ApiSuccessResult<object>(result));
        }
        [HttpGet]
        [Route("admins")]
        public async Task<IActionResult> GetAllAdmin()
        {
            var result = await _userAdminService.GetUserAdminAsync();
            return Ok(new ApiSuccessResult<object>(result));
        }

        [HttpGet]
        [Route("manager/users")]
        public async Task<IActionResult> GetAllUserOfManager(string userId)
        {
            var result = await _userAdminService.GetAllUserOfManagerAsync(userId);
            return Ok(new ApiSuccessResult<object>(result));
        }

        [HttpPost]
        [Route("manager/role")]
        public async Task<IActionResult> UpdateRoleManager(string userName)
        {
            var result = await _userAdminService.UpdateManagerAsync(userName);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }
        [HttpPost]
        [Route("admin/role")]
        public async Task<IActionResult> UpdateRoleAdmin(string userName)
        {
            var result = await _userAdminService.UpdateAdminAsync(userName);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }

        [HttpPost]
        [Route("reset-password")]
        public async Task<IActionResult> ResetPassword([FromBody] ResetPasswordAdminDto model)
        {
            model.UserUpdate = User.Identity?.Name;
            var result = await _userAdminService.ResetPassowrdAsync(model);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }

        [HttpGet]
        [Route("/api/admin/user/managerBot")]
        public async Task<IActionResult> GetUserManagerBot([FromQuery] string userId)
        {
            var result = await _userAdminService.GetUserBotAsync(userId);
            return Ok(new ApiSuccessResult<object>(result));
        }




        [HttpPost]
        [Route("/api/admin/user/managerBot/add")]
        public async Task<IActionResult> AddUserManagerBot([FromBody] UserAddBOTAdminDto model)
        {
            var result = await _userAdminService.InsertBOTOfUserAsync(model);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }



        [HttpPost]
        [Route("/api/admin/user/delete")]
        public async Task<IActionResult> DeleteUser(string userId)
        {
            var result = await _userAdminService.DeleteAsync(userId);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }
        [HttpPost]
        [Route("/api/admin/user/create")]
        public async Task<IActionResult> CreateUser([FromBody] UserCreateAdminDto model)
        {
            var result = await _userAdminService.CreateUserAsync(model);
            if (result.Key)
            {
                return Ok(new ApiSuccessResult<string>(string.Empty));
            }
            return Ok(new ApiErrorResult<string>(result.Value));
        }
    }
}
