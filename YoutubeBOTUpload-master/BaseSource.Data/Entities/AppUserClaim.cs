using Microsoft.AspNetCore.Identity;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.Data.Entities
{
    public class AppUserClaim : IdentityUserClaim<string>
    {
        public AppUser User { get; set; }
    }
}
