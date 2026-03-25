using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;
using Microsoft.Extensions.Configuration;

namespace BaseSource.Data.EF
{
    public class BaseSourceDbContextFactory : IDesignTimeDbContextFactory<BaseSourceDbContext>
    {
        public BaseSourceDbContext CreateDbContext(string[] args)
        {
            IConfigurationRoot configuration;

            try
            {
                configuration = new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile("appsettings.Development.json")
                .Build();
            }
            catch (Exception ex)
            {
                configuration = new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile("appsettings.json")
                .Build();
            }


            var connectionString = configuration.GetConnectionString("BaseSourceDbConnection");

            var optionsBuilder = new DbContextOptionsBuilder<BaseSourceDbContext>();
            optionsBuilder.UseSqlServer(connectionString).EnableSensitiveDataLogging();

            return new BaseSourceDbContext(optionsBuilder.Options);
        }
    }
}
