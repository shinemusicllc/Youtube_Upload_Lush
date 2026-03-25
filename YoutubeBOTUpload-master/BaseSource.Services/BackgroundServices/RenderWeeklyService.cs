using BaseSource.Services.Services.Render;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace BaseSource.Services.BackgroundServices
{
    public class RenderWeeklyService :IHostedService, IDisposable
    {
        private Timer _timer;

        private readonly ILogger<RenderWeeklyService> _logger;
        private readonly IServiceScopeFactory _scopeFactory;

        public RenderWeeklyService(ILogger<RenderWeeklyService> logger, IServiceScopeFactory scopeFactory)
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
            _logger.LogInformation("Timed Hosted Delete RenderHistory Service running.");

            _timer = new Timer(DoWork, null, TimeSpan.Zero,
                TimeSpan.FromHours(1));

            return Task.CompletedTask;
        }

        public Task StopAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation("Timed Hosted Delete RenderHistory Service stopping.");

            _timer?.Change(Timeout.Infinite, 0);

            return Task.CompletedTask;
        }

        private async void DoWork(object state)
        {
            _logger.LogInformation("Begin Check Session Bank Service.");
            var _renderService = _scopeFactory.CreateScope().ServiceProvider.GetRequiredService<IRenderClientService>();

            await _renderService.DeleteWeeklyAsync();
            _logger.LogInformation("End Check Session Bank Service.");
        }
    }
}
