using BaseSource.Data.Entities;
using BaseSource.Services.Services.BOT;
using BaseSource.Services.Services.ChannelAdmin;
using BaseSource.Services.Services.RenderAdmin;
using BaseSource.Shared.Enums;
using BaseSource.SharedSignalrData.Classes;
using BaseSource.SharedSignalrData.Enums;
using BaseSource.SharedSignalrData.Interfaces;
using EFCore.UnitOfWork;
using Microsoft.AspNetCore.SignalR;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Primitives;

namespace BaseSource.Services.Services.Signalr
{
    public class BotHub : Hub<IClientHub>, IServerHub
    {
        private readonly IUnitOfWork _unitOfWork;
        private readonly ILogger<BotHub> _logger;
        private readonly IChannelYoutubeAdminService _channelYoutubeAdminService;
        private readonly IRenderAdminService _renderAdminService;
        private readonly IManagerBOTService _managerBOTService;
        public BotHub(
            IUnitOfWork unitOfWork
            , ILogger<BotHub> logger
            , IChannelYoutubeAdminService channelYoutubeAdminService
            , IRenderAdminService renderAdminService
            , IManagerBOTService managerBOTService
            )
        {
            _unitOfWork = unitOfWork;
            _logger = logger;
            _channelYoutubeAdminService = channelYoutubeAdminService;
            _renderAdminService = renderAdminService;
            _managerBOTService = managerBOTService;
        }

        string BotId
        {
            get
            {
                if (this.Context.GetHttpContext()?.Request?.Headers?.TryGetValue("BotId", out StringValues strings) == true)
                {
                    return strings;
                }
                return string.Empty;
            }
        }

        public override async Task OnConnectedAsync()
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<ManagerBOT>();

                var botCurrent = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.BotId == BotId, disableTracking: false);
                if (botCurrent != null)
                {
                    botCurrent.ConnectionId = Context.ConnectionId;
                    botCurrent.Status = ManagerBOTStatus.Connected;
                    botCurrent.DeletedTime = null;
                    _repository.Update(botCurrent);
                }
                else
                {
                    _repository.Insert(new ManagerBOT
                    {
                        BotId = BotId,
                        ConnectionId = Context.ConnectionId,
                        CreatedTime = DateTime.Now
                    });
                }
                await _unitOfWork.SaveChangesAsync();

            }
            catch (Exception ex)
            {
                _logger.LogError($"Connect bot failed by error:[{ex}]");

            }
            await base.OnConnectedAsync();
        }


        public override async Task OnDisconnectedAsync(Exception? exception)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<ManagerBOT>();

                var _repositoryRender = _unitOfWork.GetRepository<RenderHistory>();

                var botCurrent = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.BotId == BotId, disableTracking: false);
                if (botCurrent != null)
                {
                    botCurrent.Status = ManagerBOTStatus.Disconnected;
                    _repository.Update(botCurrent);

                    var renderCurrents = await _repositoryRender.Queryable()
                        .Where(x => x.ChannelYoutube.ManagerBOTId == botCurrent.Id
                        && x.Status != WorkStatus.Error
                        && x.Status != WorkStatus.Cancelled
                        && x.Status != WorkStatus.Completed
                        && x.Status != WorkStatus.Schedule
                        ).ToListAsync();

                    if (renderCurrents.Any())
                    {
                        foreach (var item in renderCurrents)
                        {
                            item.Status = WorkStatus.Cancelled;
                            //item.Order = 0;
                            // item.Action = RenderAction.Cancel;
                        }
                        _repositoryRender.Update(renderCurrents);
                    }
                    await _unitOfWork.SaveChangesAsync();
                }
            }
            catch (Exception ex)
            {
                _logger.LogError($"Connect bot failed by error:[{ex}]");

            }

            await base.OnDisconnectedAsync(exception);
        }
        public async Task ChromeProfileUpdateAsync(List<ChromeProfileData> chromeProfileDatas)
        {
            await _channelYoutubeAdminService.ChromeProfileUpdateAsync(BotId, chromeProfileDatas);

        }

        public async Task WorkUpdateAsync(WorkResponse workResponse)
        {
            await _renderAdminService.WorkUpdateAsync(workResponse);
        }

        public Task BotConfigResponseAsync(BotConfig botConfig)
        {
            //r
            //throw new NotImplementedException();
            return Task.CompletedTask;
        }

        public async Task PingAsync(PingData pingData)
        {
            await _managerBOTService.UpdateSpaceDiskAsync(BotId, Context.ConnectionId, pingData);
        }
    }
}
