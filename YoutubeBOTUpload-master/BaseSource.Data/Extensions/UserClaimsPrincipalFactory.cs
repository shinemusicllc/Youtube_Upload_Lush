using BaseSource.Data.EF;
using BaseSource.Data.Entities;
using Microsoft.AspNetCore.Identity;
using Microsoft.Extensions.Options;
using System.Security.Claims;

namespace BaseSource.Data.Extensions
{
    public class UserClaimsPrincipalFactory : UserClaimsPrincipalFactory<AppUser>
    {
        private readonly BaseSourceDbContext _db;
        private readonly UserManager<AppUser> _userManager;
        private readonly RoleManager<AppRole> _roleManager;

        public UserClaimsPrincipalFactory(
            UserManager<AppUser> userManager,
            RoleManager<AppRole> roleManager,
            IOptions<IdentityOptions> optionsAccessor,
            BaseSourceDbContext db)
                : base(userManager, optionsAccessor)
        {
            _db = db;
            _userManager = userManager;
            _roleManager = roleManager;
        }

        protected override async Task<ClaimsIdentity> GenerateClaimsAsync(AppUser user)
        {
            var identity = await base.GenerateClaimsAsync(user);

            var roles = await _userManager.GetRolesAsync(user);
            //var details = await _db.UserDetails.FindAsync(user.Id);

            foreach (var roleName in roles)
            {
                identity.AddClaim(new Claim(ClaimTypes.Role, roleName));

                if (_roleManager.SupportsRoleClaims)
                {
                    var role = await _roleManager.FindByNameAsync(roleName);
                    if (role != null)
                    {
                        identity.AddClaims(await _roleManager.GetClaimsAsync(role));
                    }
                }
            }
            //identity.AddClaim(new Claim("StaffId", details.StaffId));
            //identity.AddClaim(new Claim("MaDVQL", details.MaDVQL ?? ""));

            return identity;
        }
    }
}
