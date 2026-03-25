using BaseSource.Services.Services.Render;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace BaseSource.Services.BackgroundServices
{
    public class ScheduleRenderService : IHostedService, IDisposable
    {
        private Timer _timer;

        private readonly ILogger<ScheduleRenderService> _logger;
        private readonly IServiceScopeFactory _scopeFactory;

        public ScheduleRenderService(ILogger<ScheduleRenderService> logger, IServiceScopeFactory scopeFactory)
        {

            _logger = logger;
            _scopeFactory = scopeFactory;
        }

        public void Dispose()
        {
            _timer?.Dispose();
        }
        public Task StartAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation("Timed Hosted ScheduleRenderAsync Service running.");

            _timer = new Timer(DoWork, null, TimeSpan.Zero,
                TimeSpan.FromSeconds(8));

            return Task.CompletedTask;
        }

        public Task StopAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation("Timed Hosted ScheduleRenderAsync Service stopping.");

            _timer?.Change(Timeout.Infinite, 0);

            return Task.CompletedTask;
        }

        private async void DoWork(object state)
        {
          //  _logger.LogInformation("Begin Check ScheduleRenderAsync Service.");
            var _renderService = _scopeFactory.CreateScope().ServiceProvider.GetRequiredService<IRenderClientService>();

            await _renderService.ScheduleRenderAsync();
           // _logger.LogInformation("End Check ScheduleRenderAsync Service.");
        }
    }
}
