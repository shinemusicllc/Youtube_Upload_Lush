using BaseSource.Data.Entities;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;

namespace BaseSource.Data.Extensions
{
    public static class ModelBuilderExtensions
    {
        public static void Seed(this ModelBuilder modelBuilder)
        {
            // Identity data
            var roleAdminId = (new Guid("c1105ce5-9dbc-49a9-a7d5-c963b6daa62a")).ToString();

            modelBuilder.Entity<AppRole>().HasData(
                new AppRole
                {
                    Id = roleAdminId,
                    Name = "Admin",
                    NormalizedName = "Admin",
                    Description = "Administrator role"
                });

            var userAdminId = (new Guid("ffded6b0-3769-4976-841b-69459049a62d")).ToString();
            var hasher = new PasswordHasher<AppUser>();
            modelBuilder.Entity<AppUser>().HasData(new AppUser
            {
                Id = userAdminId,
                UserName = "superadmin",
                NormalizedUserName = "superadmin",
                Email = "admin@gmail.com",
                NormalizedEmail = "admin@gmail.com",
                EmailConfirmed = true,
                PasswordHash = hasher.HashPassword(null, "12345678"),
                SecurityStamp = string.Empty
            });

            modelBuilder.Entity<AppUserRole>().HasData(new AppUserRole
            {
                RoleId = roleAdminId,
                UserId = userAdminId
            });


            ////add permission admin
            //var roleClaims = new List<AppRoleClaim>();
            //var idIndex = 1;
            //foreach (var permissionModule in PermissionModules.GetAllPermissionsModules())
            //{
            //    foreach (var permission in PermissionModules.GeneratePermissionsForModule(permissionModule))
            //    {
            //        roleClaims.Add(new AppRoleClaim
            //        {
            //            Id = idIndex++,
            //            RoleId = roleAdminId,
            //            ClaimType = Permissions.PermissionType,
            //            ClaimValue = permission
            //        });
            //    }
            //}
            //modelBuilder.Entity<AppRoleClaim>().HasData(roleClaims);
        }
    }
}
