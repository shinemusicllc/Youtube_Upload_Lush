using AutoMapper;
using BaseSource.Shared.Enums;
using BaseSource.Data.EF;
using BaseSource.Data.Entities;
using BaseSource.ViewModels.ManagerBOT;
using BaseSource.ViewModels.ManagerBOTAdmin;
using EFCore.UnitOfWork;
using EFCore.UnitOfWork.PageList;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using BaseSource.SharedSignalrData.Enums;
using Microsoft.AspNetCore.SignalR;
using BaseSource.Services.Services.Signalr;
using BaseSource.SharedSignalrData.Interfaces;
using BaseSource.SharedSignalrData.Classes;

namespace BaseSource.Services.Services.BOT
{
    public class ManagerBOTService : IManagerBOTService
    {
        private readonly IUnitOfWork _unitOfWork;
        private readonly ILogger<ManagerBOTService> _logger;
        private readonly IMapper _mapper;
        private readonly IHubContext<BotHub, IClientHub> _botContextHub;
        public ManagerBOTService(
            IUnitOfWork<BaseSourceDbContext> unitOfWork,
            ILogger<ManagerBOTService> logger,
            IMapper mapper
            , IHubContext<BotHub, IClientHub> botContextHub
            )
        {
            _unitOfWork = unitOfWork;
            _logger = logger;
            _mapper = mapper;
            _botContextHub = botContextHub;
        }

        public async Task<KeyValuePair<bool, string>> ConnectedAsync(BotConnectedDto model)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<ManagerBOT>();

                var botCurrent = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.BotId == model.BotId, disableTracking: false);
                if (botCurrent != null)
                {
                    botCurrent.ConnectionId = model.ConnectionId;
                    botCurrent.Status = ManagerBOTStatus.Connected;
                    botCurrent.DeletedTime = null;
                    _repository.Update(botCurrent);
                }
                else
                {
                    _repository.Insert(new ManagerBOT
                    {
                        BotId = model.BotId,
                        ConnectionId = model.ConnectionId,
                        CreatedTime = DateTime.Now
                    });
                }
                await _unitOfWork.SaveChangesAsync();
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Connect bot failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Connect lỗi :[{ex.Message}]");
            }
        }

        public async Task<KeyValuePair<bool, string>> CreateBOTAsync(ManagerBotCreateDto model)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<Data.Entities.ManagerBOT>();

                var botCurrent = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.BotId == model.BotId,
                    disableTracking: false);

                if (botCurrent == null)
                {
                    _repository.Insert(new Data.Entities.ManagerBOT
                    {
                        BotId = model.BotId,
                        CreatedTime = DateTime.Now,
                        Group = model.Group,
                        Name = model.Name,
                        Status = ManagerBOTStatus.Connected,
                        UpdatedTime = DateTime.Now,
                    });
                }
                else
                {
                    botCurrent.ConnectionId = model.ConnectionId;
                    botCurrent.Status = ManagerBOTStatus.Connected;
                    botCurrent.UpdatedTime = DateTime.Now;
                    _repository.Update(botCurrent);
                }
                await _unitOfWork.SaveChangesAsync();

                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Create BOT failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, "Create BOT failed");
            }
        }

        public async Task<KeyValuePair<bool, string>> DeleteAsync(int id)
        {
            try
            {
                var _repositoryUser = _unitOfWork.GetRepository<AppUser>();

                var _repositoryChannel = _unitOfWork.GetRepository<ChannelYoutube>();

                var _repositoryBot = _unitOfWork.GetRepository<ManagerBOT>();
                var _repositoryRender = _unitOfWork.GetRepository<RenderHistory>();

                var botCurrent = await _repositoryBot.GetFirstOrDefaultAsync(
                    predicate: x => x.Id == id, disableTracking: false);

                if (botCurrent == null)
                {
                    return new KeyValuePair<bool, string>(false, "BOT không tồn tại!");
                }

                botCurrent.DeletedTime = DateTime.Now;
                botCurrent.Status = ManagerBOTStatus.Disconnected;

                var renders = await _repositoryRender.Queryable()
                    .Where(x => x.ChannelYoutube.ManagerBOTId == id).ToListAsync();
                if (renders != null && renders.Any())
                {
                    _repositoryRender.Delete(renders);
                }

                var channels = await _repositoryChannel.Queryable()
                    .Where(x => x.ManagerBOTId == id).ToListAsync();

                if (channels != null && channels.Any())
                {
                    _repositoryChannel.Delete(channels);
                }

                _repositoryBot.Update(botCurrent);
                await _unitOfWork.SaveChangesAsync();

                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Delete BOT failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, "Xóa BOT không thành công vui lòng thử lại!");
            }
        }

        public async Task<KeyValuePair<bool, string>> DisconnectBotAsync(string connectionId)
        {
            try
            {
                var _repositoryBot = _unitOfWork.GetRepository<ManagerBOT>();
                var _repositoryRender = _unitOfWork.GetRepository<RenderHistory>();

                var botCurrent = await _repositoryBot.GetFirstOrDefaultAsync(
                    predicate: x => x.ConnectionId == connectionId, disableTracking: false);
                if (botCurrent != null)
                {
                    botCurrent.Status = ManagerBOTStatus.Disconnected;

                    var renderCurrents = await _repositoryRender.Queryable()
                        .Where(x => x.ChannelYoutube.ManagerBOTId == botCurrent.Id
                        && x.Status != WorkStatus.Error
                        && x.Status != WorkStatus.Cancelled
                        //&& x.Status == RenderStatus.Render
                        ).ToListAsync();

                    if (renderCurrents.Any())
                    {
                        foreach (var item in renderCurrents)
                        {
                            item.Status = WorkStatus.Cancelled;
                            // item.Action = RenderAction.Cancel;
                        }
                        _repositoryRender.Update(renderCurrents);
                    }
                    _repositoryBot.Update(botCurrent);
                    await _unitOfWork.SaveChangesAsync();
                }
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Disconnect BOT failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, ex.Message);
            }
        }

        public async Task<KeyValuePair<bool, string>> DisconnectedAsync(BotConnectedDto model)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<ManagerBOT>();

                var botCurrent = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.BotId == model.BotId, disableTracking: false);
                if (botCurrent != null)
                {
                    botCurrent.Status = ManagerBOTStatus.Disconnected;
                    _repository.Update(botCurrent);
                    await _unitOfWork.SaveChangesAsync();
                }


                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Connect bot failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Connect lỗi :[{ex.Message}]");
            }
        }

        public async Task<IPagedList<ManagerBotInfoDto>> GetBOTByFilterAsync(ManagerBOTRequestDto model, string userId, bool isAdmin = false)
        {
            var _repository = _unitOfWork.GetRepository<ManagerBOT>();
            var _repositoryUserChannel = _unitOfWork.GetRepository<UserChannel>();
            var _repositoryRender = _unitOfWork.GetRepository<RenderHistory>();
            var query = _repository.Queryable().AsNoTracking();

            if (!isAdmin)
            {
                query = query.Where(x => x.UserIdManager == userId);
            }
            else
            {
                var lstManagers = new List<string>();
                if (!string.IsNullOrWhiteSpace(model.Managers))
                {
                    lstManagers = model.Managers.Split(',').ToList();
                }
                if (lstManagers.Any())
                {
                    query = query.Where(x => lstManagers.Any(i => i == x.UserIdManager));
                }
            }
            query = query.Where(x => x.DeletedTime == null);
            try
            {
                return await _repository.GetStagesPagedListAsync(
                stages: query,
                selector: x => new ManagerBotInfoDto
                {
                    BotId = x.BotId,
                    Id = x.Id,
                    CreatedTime = x.CreatedTime,
                    Group = x.Group,
                    Name = x.Name,
                    Status = x.Status,
                    UsageDisk = x.UsageDisk,
                    SpaceDisk = x.SpaceDisk,
                    Bandwidth = x.Bandwidth,
                    CPU = x.CPU,
                    RAM = x.RAM,
                    NumberOfThreads = x.NumberOfThreads,
                    UserIdManager = x.UserIdManager,
                    UserManager = x.User.UserName,
                    NumberOfThreadsInRun = _repositoryRender.Queryable().AsNoTracking()
                    .Where(i => i.ChannelYoutube.ManagerBOTId == x.Id
                    && (i.Status == WorkStatus.Downloading
                    || i.Status == WorkStatus.Rendering
                    || i.Status == WorkStatus.Uploading)).Count(),
                    //NumberOfThreadsInRun = x.ChannelYoutubes
                    //.Sum(i => i.RenderHistorys
                    //.Where(o => o.Status != WorkStatus.Completed
                    //&& o.Status != WorkStatus.Cancelled
                    //&& o.Status != WorkStatus.Error).Count()),
                    TotalChannel = x.ChannelYoutubes.Count(),
                    //TotalUser = x.ChannelYoutubes.Sum(i => i.UserChannels.Select(o => o.UserId).Distinct().Count())
                    TotalUser = _repositoryUserChannel.Queryable().AsNoTracking()
                        .Where(o => o.ChannelYoutube.ManagerBOTId == x.Id).Select(o => o.UserId).Distinct().Count(),
                }, orderBy: x => x.OrderByDescending(i => i.CreatedTime), pageIndex: model.Page, pageSize: model.PageSize);

            }
            catch (Exception ex)
            {

                throw;
            }


        }

        public async Task<List<ManagerBotInfoDto>> GetBotByUserIdAsync(string userId)
        {
            try
            {
                var _repositoryUserChannel = _unitOfWork.GetRepository<UserChannel>();
                var _repository = _unitOfWork.GetRepository<ManagerBOT>();
                return await _repository.Queryable().AsNoTracking()
                    .Where(x => x.DeletedTime == null
                    && x.ChannelYoutubes.Any(i => i.UserChannels.Any(o => o.UserId == userId)))
                    .Select(x => new ManagerBotInfoDto
                    {
                        Id = x.Id,
                        BotId = x.BotId,
                        Name = x.Name,
                        Group = x.Group,
                        Status = x.Status,
                        CreatedTime = x.CreatedTime,
                        TotalChannel = x.ChannelYoutubes.Count(),
                        NumberOfThreads = x.NumberOfThreads,
                        UsageDisk = x.UsageDisk,
                        SpaceDisk = x.SpaceDisk,
                        Bandwidth = x.Bandwidth,
                        CPU = x.CPU,
                        RAM = x.RAM,
                        TotalUser = _repositoryUserChannel.Queryable().AsNoTracking()
                        .Where(o => o.ChannelYoutube.ManagerBOTId == x.Id).Select(o => o.UserId).Distinct().Count()
                    }).ToListAsync();
                //if (data != null && data.Any())
                //{
                //    foreach (var item in data)
                //    {
                //        item.TotalUser = await _repositoryUserChannel.Queryable().AsNoTracking()
                //        .Where(o => o.ChannelYoutube.ManagerBOTId == item.Id).Select(o => o.UserId).Distinct().CountAsync();
                //    }
                //}
                //return data;
            }
            catch (Exception ex)
            {

                throw;
            }

        }

        public async Task<ManagerBotInfoDto> GetByIdAsync(int id)
        {
            var _repository = _unitOfWork.GetRepository<ManagerBOT>();
            return await _repository.Queryable().AsNoTracking()
                .Where(x => x.Id == id && x.DeletedTime == null)
                .Select(x => new ManagerBotInfoDto
                {
                    Id = x.Id,
                    BotId = x.BotId,
                    Name = x.Name,
                    Group = x.Group,

                }).FirstOrDefaultAsync();
        }

        public async Task<List<UserManagerBotAdminInfoDto>> GetUserOfBotIdAsync(int botId)
        {
            var _repository = _unitOfWork.GetRepository<AppUser>();
            return await _repository.Queryable().AsNoTracking()
                .Where(x => x.UserChannels.Any(i => i.ChannelYoutube.ManagerBOTId == botId))
                .Select(x => new UserManagerBotAdminInfoDto
                {
                    Password = x.Password,
                    UserId = x.Id,
                    UserName = x.UserName,
                    TotalChannel = x.UserChannels.Count(),
                    TotalBot = x.UserChannels.Select(i => i.ChannelYoutube.ManagerBOTId).Distinct().Count()
                }).ToListAsync();
        }

        public async Task<KeyValuePair<bool, string>> UpdateBOTAsync(int id, ManagerBotUpdateDto model, string userId, bool isAdmin)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<ManagerBOT>();
                var _repositoryUserChannel = _unitOfWork.GetRepository<UserChannel>();
                var _repositoryRender = _unitOfWork.GetRepository<RenderHistory>();

                var botCurrent = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.Id == id, disableTracking: false);
                if (botCurrent == null)
                {
                    return new KeyValuePair<bool, string>(false, "Dữ liệu không tồn tại!");
                }
                botCurrent.Name = model.Name;
                botCurrent.Group = model.Group;
                if (isAdmin)
                {
                    if (botCurrent.UserIdManager != model.UserIdManager && !string.IsNullOrWhiteSpace(model.UserIdManager))
                    {
                        botCurrent.UserIdManager = model.UserIdManager;

                        var renders = await _repositoryRender.Queryable()
                        .Where(x => x.ChannelYoutube.ManagerBOTId == model.Id)
                        .Include(x => x.ChannelYoutube)
                        .ThenInclude(o => o.ManagerBOT)
                        .ToListAsync();

                        if (renders != null && renders.Any())
                        {
                            foreach (var item in renders)
                            {
                                item.Status = WorkStatus.Cancelled;
                                await _botContextHub
                                .Clients
                                .Client(item.ChannelYoutube.ManagerBOT.ConnectionId)
                                .CancelWorkAsync(new Identy
                                {
                                    ItemId = item.Id
                                });
                            }
                            //_repositoryRender.Update(renders);
                            // await _unitOfWork.SaveChangesAsync();
                        }

                        var channels = await _repositoryUserChannel.Queryable()
                        .Where(x => x.ChannelYoutube.ManagerBOTId == model.Id)
                        .ToListAsync();
                        if (channels.Any())
                        {
                            _repositoryUserChannel.Delete(channels);
                        }
                    }

                }
                _repository.Update(botCurrent);

                await _unitOfWork.SaveChangesAsync();

                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Update BOT Failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Cập nhật không thành công:[{ex.Message}]");
            }
        }

        public async Task<KeyValuePair<bool, string>> UpdateSpaceDiskAsync(string botId, string connectionId, PingData model)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<ManagerBOT>();
                var botCurrent = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.BotId == botId, disableTracking: false);
                if (botCurrent != null)
                {
                    botCurrent.SpaceDisk = model.StorageTotal;
                    botCurrent.UsageDisk = model.StorageCurrent;
                    botCurrent.Status = ManagerBOTStatus.Connected;
                    botCurrent.Bandwidth = model.Bandwidth;
                    botCurrent.ConnectionId = connectionId;
                    botCurrent.DeletedTime = null;
                    _repository.Update(botCurrent);
                    await _unitOfWork.SaveChangesAsync();
                }

                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"UpdateSpaceDiskAsync failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
        }

        public Task<KeyValuePair<bool, string>> UpdateStatusAsync(int id, ManagerBOTStatus Status)
        {
            throw new NotImplementedException();
        }

        public async Task<KeyValuePair<bool, string>> UpdateThreadAsync(BotUpdateThreadDto model, string userId, bool isAdmin = false)
        {
            try
            {
                var _repositoryChannel = _unitOfWork.GetRepository<ChannelYoutube>();

                var _repositoryRender = _unitOfWork.GetRepository<RenderHistory>();
                var _repository = _unitOfWork.GetRepository<ManagerBOT>();

                var botCurrent = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.Id == model.Id, disableTracking: false);
                if (botCurrent == null)
                {
                    return new KeyValuePair<bool, string>(false, "Dữ liệu không tồn tại!");
                }

                botCurrent.NumberOfThreads = model.Thread;


                //send data to Bot

                botCurrent.UpdatedTime = DateTime.Now;
                _repository.Update(botCurrent);

                await _unitOfWork.SaveChangesAsync();

                await _botContextHub
                    .Clients
                    .Client(botCurrent.ConnectionId)
                    .ChangeBotConfigAsync(new BotConfig { ThreadCount = botCurrent.NumberOfThreads });
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Update Thread Bot failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Cập nhật không thành công:[{ex.Message}]");
            }
        }
    }
}
