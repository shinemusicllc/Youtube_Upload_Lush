using BaseSource.Shared.Enums;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.ViewModels.ManagerBOTAdmin
{
    public class ManagerBotAdminInfoDto
    {
        public int Id { get; set; }
        public string BotId { get; set; }
        public string BotName { get; set; }
        public string Group { get; set; }
        public ManagerBOTStatus Status { get; set; }
        public int TotalChannel { get; set; }
        public int TotalUser { get; set; }
    }
    public class ManagetBotAdminUpdateDto
    {
        public int Id { get; set; }
        public string BotName { get; set; }
        public string Group { get; set; }
    }
    public class UserManagerBotAdminInfoDto
    {
        public string UserId { get; set; }
        public string UserName { get; set; }
        public string Password { get; set; }
        public int TotalChannel { get; set; }
        public int TotalBot { get; set; }
    }
}
