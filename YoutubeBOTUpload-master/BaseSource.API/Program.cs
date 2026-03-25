using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using BaseSource.API.Cofigurations;
using EFCore.UnitOfWork;
using BaseSource.Data.EF;
using BaseSource.Data.Entities;
using BaseSource.Shared.Constants;
using BaseSource.SharedSignalrData;
using BaseSource.Services.Services.Signalr;
using BaseSource.Services.BackgroundServices;

var builder = WebApplication.CreateBuilder(args);

//add logging
builder.Host.ConfigureLogging(logging =>
{
    logging.ClearProviders();
    logging.AddFilter("Microsoft.EntityFrameworkCore", LogLevel.Warning);
    logging.AddLog4Net();
    // logging.AddFilter("Microsoft.EntityFrameworkCore", LogLevel.Information);

});

//add db context and unitOfwork
builder.Services.AddDbContext<BaseSourceDbContext>(options => options.UseSqlServer(builder.Configuration.GetConnectionString(SystemConstants.MainConnectionString)))
                .AddUnitOfWork<BaseSourceDbContext>();

builder.Services.AddIdentity<AppUser, AppRole>()
                .AddEntityFrameworkStores<BaseSourceDbContext>()
                .AddDefaultTokenProviders();

builder.Services.Configure<IdentityOptions>(options =>
{
    options.Password.RequireDigit = false;
    options.Password.RequiredLength = 6;
    options.Password.RequireLowercase = false;
    options.Password.RequireUppercase = false;
    options.Password.RequireNonAlphanumeric = false;
});
//AddAuthorization
//builder.Services.AuthorizationPolyConfiguration();
//Declare DI
builder.Services.DIConfiguration();



// Add services to the container.

builder.Services.AddControllers();

builder.Services.AddHostedService<RenderWeeklyService>();
builder.Services.AddHostedService<ScheduleRenderService>();
//add autoMapper
builder.Services.AddAutoMapper(AppDomain.CurrentDomain.GetAssemblies());

// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
// Register the Swagger generator, defining 1 or more Swagger documents
builder.Services.SwaggerConfiguration(builder.Configuration);

builder.Services.AddSignalR().AddJsonProtocol(configure => configure.PayloadSerializerOptions.SignalR_JsonSerializerOptions());


builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(
        builder =>
        {
            builder
                .AllowAnyMethod()
                .AllowAnyHeader()
                .SetIsOriginAllowed(origin => true)
                .AllowCredentials();
        });
});



var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseAuthentication();
app.UseRouting();

app.UseAuthorization();
// UseCors must be called before MapHub.
app.UseCors();
app.MapControllers();

app.UseEndpoints(endpoints =>
{
    endpoints.MapHub<WebHub>("/WebHub");
    endpoints.MapHub<BotHub>("/BotHub");
});

app.Run();
