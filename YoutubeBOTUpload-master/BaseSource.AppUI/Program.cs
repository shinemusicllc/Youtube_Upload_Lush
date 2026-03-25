using BaseSource.Shared.Constants;
using BaseSource.AppUI.Configuration;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Http.Features;
using System.Net.Http.Headers;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllersWithViews();

//config session
builder.Services.AddDistributedMemoryCache();
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromDays(15);
});

builder.Services.AddHttpClient();
builder.Services.AddHttpClient(SystemConstants.BackendApiClient, (sp, httpClient) =>
{
    httpClient.BaseAddress = new Uri(builder.Configuration.GetValue<string>("BackendApiBaseAddress"));

    // Find the HttpContextAccessor service
    var httpContextAccessor = sp.GetRequiredService<IHttpContextAccessor>();

    // Get the bearer token from the request context
    var bearerToken = httpContextAccessor.HttpContext.Request.Cookies[SystemConstants.Token];

    // Add authorization if found
    if (bearerToken != null)
    {
        httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", bearerToken);
    }
    //httpClient.DefaultRequestHeaders.Add("Accept-Language", httpContextAccessor.HttpContext.Request.Cookies[SystemConstants.LanguageCulture]?.Substring(2, 2)?.ToString() ?? SystemConstants.LanguageVietnam);
});



builder.Services.Configure<FormOptions>(options =>
{
    options.ValueLengthLimit = int.MaxValue;
    options.MultipartBodyLengthLimit = long.MaxValue; // if don't set default value is: 128 MB
    options.MultipartHeadersLengthLimit = int.MaxValue;
});

//multiple currency
builder.Services.AddControllersWithViews()
    .AddRazorRuntimeCompilation();

builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
           {
               options.LoginPath = "/auth/login";
               options.AccessDeniedPath = "/User/Forbidden/";
           });

builder.Services.ConfigureApplicationCookie(options =>
           {
               options.AccessDeniedPath = "/auth/login";
               options.ExpireTimeSpan = TimeSpan.FromDays(15);
               options.LoginPath = "/auth/login";
           });

//Declare DI
builder.Services.DIConfiguration();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}
app.UseSession();
app.UseRequestLocalization();
app.UseAuthentication();
app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

//app.MapControllerRoute(
//    name: "default",
//    pattern: "{controller=Home}/{action=Index}/{id?}");
app.UseEndpoints(endpoints =>
           {
               endpoints.MapControllerRoute(
                  name: "areas",
                  pattern: "{area:exists}/{controller=Home}/{action=Index}/{id?}"
                );
               //endpoints.MapControllerRoute(name: "support",
               //    pattern: "support/{*article}",
               //    defaults: new { controller = "Support", action = "ArticleCategory" });
               endpoints.MapControllerRoute(
                   name: "default",
                   pattern: "{controller=Home}/{action=Index}/{id?}");
           });

app.Run();
