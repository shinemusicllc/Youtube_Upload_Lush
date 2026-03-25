
using BaseSource.Shared.Enums;
using BaseSource.ViewModels.Common;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.ViewModels.UserAdmin
{
    public class UserAdminInfoDto
    {
        public string Id { get; set; }
        public string UserName { get; set; }
        public string Email { get; set; }
        public string LinkFB { get; set; }
        public string LinkTelegram { get; set; }
        public DateTime CreatedTime { get; set; }
        public string TelegramAPI { get; set; }
        public string Password { get; set; }
        public int TotalBOT { get; set; }
        public int TotalChannel { get; set; }
        public DateTime? UpdatedTime { get; set; }
        public string UserUpdate { get; set; }
        public string UserIdManager { get; set; }
        public string UserManager { get; set; }
        public List<string> Roles { get; set; }
    }
    public class UserAdminRequestDto : PageQuery
    {
        public string UserName { get; set; }
        public bool IsOrder { get; set; }
        public string Managers { get; set; }
    }
    public class UserGroupDto
    {
        public string UserId { get; set; }
        public string UserName { get; set; }
        public string UserManagerId { get; set; }
    }
    public class UserGroupAddDto
    {
        public string UserName { get; set; }
        public string UserManagerId { get; set; }
    }
    public class UserGroupDeleteDto : UserGroupAddDto
    {

    }
    public class ResetPasswordAdminDto
    {
        public string UserUpdate { get; set; }
        public string UserId { get; set; }
        public string Password { get; set; }
    }
    public class UserManagerBotDto
    {
        public string UserId { get; set; }
        public int NumberOfThreads1080 { get; set; }
        public int NumberOfThreads4K { get; set; }
        public int? Bot1080 { get; set; }
        public int? Bot4K { get; set; }
        public string UserName { get; set; }
    }

    public class UserManagerBotInfoDto
    {
        public int Id { get; set; }
        public int NumberOfThreads { get; set; }
        public int NumberOfThreadsInRun { get; set; }
        public string BotName { get; set; }
        public string UserName { get; set; }
        public LiveType? LiveType { get; set; }
    }

    public class UserCreateAdminDto
    {
        public string UserName { get; set; }
        public string Password { get; set; }
        public int NumberOfThreads1080 { get; set; }
        public int NumberOfThreads4K { get; set; }
        public string LinkTelegram { get; set; }
        public string UserIdManager { get; set; }
    }
    public class UserManagerBotUpdateDto
    {
        public int Id { get; set; }
        public int NumberOfThreads { get; set; }
        public string UserId { get; set; }
        public string UserName { get; set; }
    }
    public class UserAddBOTAdminDto
    {
        public string UserId { get; set; }
        public string UserName { get; set; }
        public int NumberOfThreads { get; set; }
        public int? TypeBot { get; set; }
        public int? Bot1080 { get; set; }
        public int? Bot4k { get; set; }
    }
    public class UpdateTelegramDto
    {
        public string UserId { get; set; }
        public string Telegram { get; set; }
        public string UserIdManager { get; set; }
    }
}
