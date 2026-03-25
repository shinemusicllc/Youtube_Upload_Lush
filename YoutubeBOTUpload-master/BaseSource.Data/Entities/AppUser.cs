using Microsoft.AspNetCore.Identity;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.Data.Entities
{
    public class AppUser : IdentityUser<string>
    {
        public string LinkFB { get; set; }
        public string LinkTelegram { get; set; }
        public DateTime CreatedTime { get; set; }
        public string TelegramAPI { get; set; }

        public string Password { get; set; }
        public DateTime? DeletedTime { get; set; }
        public DateTime? UpdatedTime { get; set; }
        public string UserUpdate { get; set; }
        public string UserIdManager { get; set; }

        [ForeignKey("UserIdManager")]
        public AppUser? Manager { get; set; }

        public ICollection<AppUserRole> UserRoles { get; set; }
        public ICollection<AppUserClaim> Claims { get; set; }
        public ICollection<AppUserToken> Tokens { get; set; }
        public ICollection<AppUserLogin> AppUserLogins { get; set; }

        public ICollection<RenderHistory> RenderHistorys { get; set; }
        public ICollection<UserChannel> UserChannels { get; set; }
        public ICollection<ManagerBOT> ManagerBOTs { get; set; }
    }
}
