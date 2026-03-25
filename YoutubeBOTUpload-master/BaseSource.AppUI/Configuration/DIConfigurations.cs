

using BaseSource.ApiIntegration.WebApi.Channel;
using BaseSource.ApiIntegration.WebApi.ChannelAdmin;
using BaseSource.ApiIntegration.WebApi.ManagerBOT;
using BaseSource.ApiIntegration.WebApi.Render;
using BaseSource.ApiIntegration.WebApi.RenderAdmin;
using BaseSource.ApiIntegration.WebApi.Report;
using BaseSource.ApiIntegration.WebApi.Setting;
using BaseSource.ApiIntegration.WebApi.User;
using BaseSource.ApiIntegration.WebApi.UserAdmin;

namespace BaseSource.AppUI.Configuration
{
    public static class DIConfigurations
    {
        public static IServiceCollection DIConfiguration(this IServiceCollection services)
        {
            //DI for user
            //DI for user
            services.AddTransient<IUserApiClient, UserApiClient>();

            services.AddSingleton<IHttpContextAccessor, HttpContextAccessor>();

            //services.AddTransient<IServicePackageApiClient, ServicePackageApiClient>();
            //services.AddTransient<IServicePackageByMonthApiClient, ServicePackageByMonthApiClient>();
            services.AddTransient<IConfigSettingApiClient, ConfigSettingApiClient>();

            //services.AddTransient<IOrderApiClient, OrderApiClient>();

            //services.AddTransient<IOrderAdminApiClient, OrderAdminApiClient>();

            //services.AddTransient<IStreamApiClient, StreamApiClient>();

            //services.AddTransient<IManagerBOTApiClient, ManagerBOTApiClient>();
            //services.AddTransient<IStreamAdminApiClient, StreamAdminApiClient>();
            services.AddTransient<IUserAdminApiClient, UserAdminApiClient>();


            services.AddTransient<IChannelApiClient, ChannelApiClient>();
            services.AddTransient<IChannelAdminApiClient, ChannelAdminApiClient>();

            services.AddTransient<IManagerBOTApiClient, ManagerBOTApiClient>();

            services.AddTransient<IRenderApiClient, RenderApiClient>();

            services.AddTransient<IRenderAdminApiClient, RenderAdminApiClient>();
            services.AddTransient<IReportApiClient, ReportApiClient>();

            

            return services;
        }
    }
}
