using BaseSource.Services.Services.User;
using BaseSource.Services.Services.UserAdmin;
using BaseSource.Data.Entities;
using BaseSource.Services.Services.BOT;
using BaseSource.Services.Services.Channel;
using BaseSource.Services.Services.ChannelAdmin;
using BaseSource.Services.Services.Render;
using BaseSource.Services.Services.RenderAdmin;
using BaseSource.Services.Services.Report;
using BaseSource.Services.Services.Setting;
using Microsoft.AspNetCore.Identity;
using BaseSouce.Services.Services.ValidateLink;

namespace BaseSource.API.Cofigurations
{
    public static class DIConfigurations
    {
        public static IServiceCollection DIConfiguration(this IServiceCollection services)
        {
            //DI for user
            services.AddTransient<UserManager<AppUser>, UserManager<AppUser>>();
            services.AddTransient<SignInManager<AppUser>, SignInManager<AppUser>>();
            services.AddTransient<RoleManager<AppRole>, RoleManager<AppRole>>();

            services.AddTransient<IUserService, UserService>();
            services.AddTransient<IUserAdminService, UserAdminService>();

            services.AddTransient<IConfigSettingService, ConfigSettingService>();
            services.AddTransient<IRenderAdminService, RenderAdminService>();
            services.AddTransient<IChannelYoutubeAdminService, ChannelYoutubeAdminService>();
            services.AddTransient<IManagerBOTService, ManagerBOTService>();

            services.AddTransient<IChannelYoutubeClientService, ChannelYoutubeClientService>();

            services.AddTransient<IRenderClientService, RenderClientService>();
            services.AddTransient<IValidateLinkService, ValidateLinkService>();
            services.AddTransient<IReportService, ReportService>();

            
            return services;
        }
    }
}
