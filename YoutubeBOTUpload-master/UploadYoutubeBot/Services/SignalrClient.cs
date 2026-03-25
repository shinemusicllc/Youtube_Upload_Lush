using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Threading;
using System.Data.Common;
using System.Net.Http;
using System.Security.Policy;
using BaseSource.SharedSignalrData.Interfaces;
using BaseSource.SharedSignalrData.Classes;
using BaseSource.SharedSignalrData.Enums;
using BaseSource.SharedSignalrData;
using UploadYoutubeBot.UI.ViewModels;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.AspNetCore.SignalR.Client;
using TypedSignalR.Client;
using UploadYoutubeBot.Enums;

namespace UploadYoutubeBot.Services
{
    class SignalrClient : IAsyncDisposable, IDisposable
    {
        class RetryPolicy : IRetryPolicy
        {
            public TimeSpan? NextRetryDelay(RetryContext retryContext)
            {
                return TimeSpan.FromSeconds(3);
            }
        }

        class ClientHub : IClientHub
        {
            readonly SignalrClient _signalrClient;
            internal ClientHub(SignalrClient signalrClient)
            {
                this._signalrClient = signalrClient ?? throw new ArgumentNullException(nameof(signalrClient));
            }

            public Task CancelWorkAsync(Identy identy)
            {
                _signalrClient.OnCancelWorkCommand?.Invoke(identy);
                return Task.CompletedTask;
            }

            public Task ChangeBotConfigAsync(BotConfig botConfig)
            {
                _signalrClient.OnChangeBotConfigCommand?.Invoke(botConfig);
                return Task.CompletedTask;
            }

            public Task DeleteProfilesAsync(IReadOnlyList<string> profileIds)
            {
                _signalrClient.OnDeleteProfilesCommand?.Invoke(profileIds);
                return Task.CompletedTask;
            }

            public Task GetInfoChannelAsync(string profileId)
            {
                _signalrClient.OnGetInfoChannelCommand?.Invoke(profileId);
                return Task.CompletedTask;
            }

            public Task PushWorkAsync(WorkData workData)
            {
                _signalrClient.OnPushWorkCommand?.Invoke(workData);
                return Task.CompletedTask;
            }
        }

        class SafeServerHub : IServerHub
        {
            readonly IServerHub _baseServerHub;
            internal SafeServerHub(IServerHub baseServerHub)
            {
                this._baseServerHub = baseServerHub ?? throw new ArgumentNullException(nameof(baseServerHub));
            }

            public async Task BotConfigResponseAsync(BotConfig botConfig)
            {
                try
                {
                    await _baseServerHub.BotConfigResponseAsync(botConfig);
                }
                catch (Exception ex)
                {
                    if (ex is AggregateException ae) ex = ae.InnerException;

                    MainWVM.WriteExceptionLog(ex);

                    ThreadPool.QueueUserWorkItem((o) =>
                    {
                        Task.Delay(500).ContinueWith((t) =>
                        {
                            _ = this.BotConfigResponseAsync(botConfig);
                        });
                    });
                }
            }

            public async Task ChromeProfileUpdateAsync(List<ChromeProfileData> chromeProfileDatas)
            {
                try
                {
                    await _baseServerHub.ChromeProfileUpdateAsync(chromeProfileDatas);
                }
                catch (Exception ex)
                {
                    MainWVM.WriteExceptionLog(ex);

                    ThreadPool.QueueUserWorkItem((o) =>
                    {
                        Task.Delay(500).ContinueWith((t) =>
                        {
                            _ = this.ChromeProfileUpdateAsync(chromeProfileDatas);
                        });
                    });
                }
            }

            public async Task PingAsync(PingData pingData)
            {
                try
                {
                    await _baseServerHub.PingAsync(pingData);
                }
                catch (Exception ex)
                {
                    MainWVM.WriteExceptionLog(ex);
                }
            }

            public async Task WorkUpdateAsync(WorkResponse workResponse)
            {
                try
                {
                    await _baseServerHub.WorkUpdateAsync(workResponse);
                }
                catch (ObjectDisposedException)
                {
                    return;
                }
                catch (Exception ex)
                {
                    MainWVM.WriteExceptionLog(ex);

                    if (workResponse.WorkStatus >= WorkStatus.Completed)//try again
                    {
                        ThreadPool.QueueUserWorkItem((o) =>
                        {
                            Task.Delay(500).ContinueWith((t) =>
                            {
                                _ = this.WorkUpdateAsync(workResponse);
                            });
                        });
                    }
                }
            }
        }

        internal event Action<WorkData> OnPushWorkCommand;
        internal event Action<Identy> OnCancelWorkCommand;
        internal event Action<BotConfig> OnChangeBotConfigCommand;
        internal event Action<string> OnGetInfoChannelCommand;
        internal event Action<IReadOnlyList<string>> OnDeleteProfilesCommand;
        internal event Action<SignalRConnectionState> OnConnectionStateChange;
        internal IServerHub ServerHub { get; }


        readonly HubConnection _connection;
        readonly IDisposable _clientSubscription;
        public SignalrClient(Uri uri, string botId)
        {
            if (uri is null) throw new ArgumentNullException(nameof(uri));
            if (string.IsNullOrWhiteSpace(botId)) throw new ArgumentNullException(nameof(botId));

            Uri hubUri = new Uri($"{uri.Scheme}://{uri.Authority}/BotHub");
            HubConnectionBuilder hubConnectionBuilder = new();
            _connection = hubConnectionBuilder
                .WithAutomaticReconnect(new RetryPolicy())
                .WithUrl(hubUri
                , (opts) =>
                {
                    opts.HttpMessageHandlerFactory = (message) =>
                    {
                        if (message is HttpClientHandler clientHandler)
                            // always verify the SSL certificate
                            clientHandler.ServerCertificateCustomValidationCallback +=
                                 (sender, certificate, chain, sslPolicyErrors) => { return true; };
                        return message;
                    };
                    opts.Headers = new Dictionary<string, string>()
                    {
                        { "BotId", botId }
                    };
                }
                )
                .AddJsonProtocol(configure => configure.PayloadSerializerOptions.SignalR_JsonSerializerOptions())
            .Build();

            this.ServerHub = new SafeServerHub(_connection.CreateHubProxy<IServerHub>());
            _clientSubscription = _connection.Register<IClientHub>(new ClientHub(this));

            _connection.KeepAliveInterval = TimeSpan.FromSeconds(5);
            _connection.Reconnecting += _connection_Reconnecting;
            _connection.Reconnected += _connection_Reconnected;
            _connection.Closed += _connection_Closed;
        }
        ~SignalrClient()
        {
            Dispose(false);
        }
        public async ValueTask DisposeAsync()
        {
            _clientSubscription.Dispose();
            await _connection.DisposeAsync();
            GC.SuppressFinalize(this);
        }
        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }
        void Dispose(bool disposing)
        {
            _clientSubscription.Dispose();
            _connection.DisposeAsync().ConfigureAwait(false).GetAwaiter().GetResult();
        }

        private Task _connection_Closed(Exception arg)
        {
            OnConnectionStateChange?.Invoke(SignalRConnectionState.DisConnected);
            return Task.CompletedTask;
        }

        private Task _connection_Reconnected(string arg)
        {
            OnConnectionStateChange?.Invoke(SignalRConnectionState.Connected);
            return Task.CompletedTask;
        }

        private Task _connection_Reconnecting(Exception arg)
        {
            OnConnectionStateChange?.Invoke(SignalRConnectionState.Reconnecting);
            return Task.CompletedTask;
        }
        public Task StartAsync(CancellationToken cancellationToken = default)
        {
            return _connection.StartAsync(cancellationToken);
        }
        public Task StopAsync()
        {
            return _connection.StopAsync();
        }
    }
}
