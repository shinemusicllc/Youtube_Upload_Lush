using BaseSource.Data.Entities;
using BaseSource.Data.Extensions;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;

namespace BaseSource.Data.EF
{
    public class BaseSourceDbContext : IdentityDbContext<AppUser, AppRole, string, AppUserClaim, AppUserRole, AppUserLogin, AppRoleClaim, AppUserToken>

    {
        public BaseSourceDbContext(DbContextOptions options) : base(options)
        {
        }

        protected override void OnModelCreating(ModelBuilder builder)
        {
            base.OnModelCreating(builder);
            #region Identity
            builder.Entity<AppUserClaim>().ToTable("AppUserClaims");
            builder.Entity<AppUserLogin>().ToTable("AppUserLogins");
            builder.Entity<AppUserToken>().ToTable("AppUserTokens");
            builder.Entity<AppRoleClaim>().ToTable("AppRoleClaims");



            builder.EnableAutoHistory();
            builder.ApplyConfigurationsFromAssembly(typeof(BaseSourceDbContext).Assembly);
            #endregion
            ////Data seeding
            builder.Seed();

        }


    }
}
