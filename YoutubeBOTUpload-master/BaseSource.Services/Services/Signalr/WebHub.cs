using Microsoft.AspNetCore.SignalR;

namespace BaseSource.Services.Services.Signalr
{
    public class WebHub : Hub<IWebClientHub>
    {
        public override async Task OnConnectedAsync()
        {

            await base.OnConnectedAsync();
        }

        public override async Task OnDisconnectedAsync(Exception? exception)
        {
            await base.OnDisconnectedAsync(exception);
        }
    }
}
