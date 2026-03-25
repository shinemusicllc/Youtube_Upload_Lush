using AutoMapper;
using BaseSource.Shared.Enums;
using BaseSource.Data.EF;
using BaseSource.Data.Entities;
using BaseSource.Shared.Helpers;
using BaseSource.ViewModels.Render;
using EFCore.UnitOfWork;
using EFCore.UnitOfWork.PageList;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using TqkLibrary.Net.CloudStorage.GoogleDrive;
using BaseSource.SharedSignalrData.Enums;
using Microsoft.AspNetCore.SignalR;
using BaseSource.Services.Services.Signalr;
using BaseSource.SharedSignalrData.Interfaces;
using BaseSource.SharedSignalrData.Classes;
using BaseSource.ViewModels.Report;
using BaseSouce.Services.Services.ValidateLink;

namespace BaseSource.Services.Services.Render
{
    public class RenderClientService : IRenderClientService
    {
        private readonly IUnitOfWork _unitOfWork;
        private readonly ILogger<RenderClientService> _logger;
        private readonly IMapper _mapper;
        private readonly IHubContext<BotHub, IClientHub> _botContextHub;
        private readonly IValidateLinkService _validateLinkService;
        public RenderClientService(
            IUnitOfWork<BaseSourceDbContext> unitOfWork,
            ILogger<RenderClientService> logger,
            IMapper mapper
            , IHubContext<BotHub, IClientHub> botContextHub,
            IValidateLinkService validateLinkService
            )
        {
            _unitOfWork = unitOfWork;
            _logger = logger;
            _mapper = mapper;
            _botContextHub = botContextHub;
            _validateLinkService = validateLinkService;
        }


        public async Task<KeyValuePair<bool, string>> CloneAsync(string userId, int id)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<RenderHistory>();

                var renderEntity = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.Id == id && x.UserId == userId, disableTracking: true);

                if (renderEntity == null)
                {
                    return new KeyValuePair<bool, string>(false, "Dữ liệu không tồn tại!");
                }

                _repository.Insert(new RenderHistory
                {
                    AudioLoop = renderEntity.AudioLoop,
                    ChannelYoutubeId = renderEntity.ChannelYoutubeId,
                    CreatedTime = DateTime.Now,
                    //Action = RenderAction.Waiting,
                    Intro = renderEntity.Intro,
                    Outtro = renderEntity.Outtro,
                    Order = 0,
                    Status = WorkStatus.Pending,
                    VideoName = renderEntity.VideoName,
                    //TimeRenderLong= ModelB
                    //TimeRender = renderEntity.TimeRender,
                    UserId = renderEntity.UserId,
                    VideoLoop = renderEntity.VideoLoop,
                });

                await _unitOfWork.SaveChangesAsync();
                return new KeyValuePair<bool, string>(true, string.Empty);

            }
            catch (Exception ex)
            {
                _logger.LogError($"Clone Render [{id}] failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Clone Render không thành công:[{ex.Message}]");
            }
        }

        public async Task<KeyValuePair<bool, string>> CreateAsync(string userId, RenderCreateDto model)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<RenderHistory>();
                var renderCreate = new RenderHistory
                {
                    CreatedTime = DateTime.Now,
                    UserId = userId,
                    ChannelYoutubeId = model.ChannelId,
                    Intro = model.Intro,
                    VideoLoop = model.VideoLoop,
                    AudioLoop = model.AudioLoop,
                    VideoName = model.VideoName,
                    Order = 0,
                    Outtro = model.Outtro,
                    // Action = RenderAction.Waiting,
                    TimeRenderLong = model.TimeRender.Ticks,
                    //TimeRender = model.TimeRender,
                    Status = WorkStatus.Queueing,
                    ScheduleTime = model.ScheduleTime
                };

                if (renderCreate.ScheduleTime != null && renderCreate.ScheduleTime > DateTime.Now)
                {
                    renderCreate.Status = WorkStatus.Schedule;
                }

                _repository.Insert(renderCreate);

                await _unitOfWork.SaveChangesAsync();

                //renderCreate.TimeRender = new TimeSpan(renderCreate.TimeRenderLong);
                if (renderCreate.Status != WorkStatus.Schedule)
                {
                    var result = await StartAsync(userId, renderCreate.Id);
                    if (result.Key)
                    {
                        return new KeyValuePair<bool, string>(true, string.Empty);
                    }
                    return result;
                }
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Create Render failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Tạo mới không thành công, vui lòng thử lại[{ex.Message}]!");
            }
        }

        public async Task<KeyValuePair<bool, string>> DeleteAsync(string userId, int id)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<RenderHistory>();

                var renderEntity = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.Id == id && x.UserId == userId, disableTracking: false);

                if (renderEntity == null)
                {
                    return new KeyValuePair<bool, string>(false, "Dữ liệu không tồn tại!");
                }

                renderEntity.DeletedTime = DateTime.Now;
                _repository.Update(renderEntity);

                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Delete Render failed by error:[{ex}]");

                return new KeyValuePair<bool, string>(false, $"Xóa dữ liệu không thành công [{ex.Message}]");
            }
        }

        public async Task<KeyValuePair<bool, string>> DeleteWeeklyAsync()
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<RenderHistory>();

                var timeCheck = DateTime.Now.AddDays(-5);
                var datas = await _repository.Queryable()
                    .Where(x => x.CreatedTime < timeCheck
                    && (x.Status == WorkStatus.Completed
                    || x.Status == WorkStatus.Error
                    || x.Status == WorkStatus.Cancelled))
                    .ToListAsync();
                if (datas.Any())
                {
                    _repository.Delete(datas);
                    await _unitOfWork.SaveChangesAsync();
                }
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"DeleteWeeklyAsync failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
        }

        public async Task<IPagedList<RenderHistoryDto>> GetByFilterAsync(string userId, RenderRequestDto model)
        {
            var _repository = _unitOfWork.GetRepository<RenderHistory>();

            var query = _repository.Queryable().AsNoTracking();
            query = query.Where(x => x.UserId == userId && x.DeletedTime == null);
            return await _repository.GetStagesPagedListAsync(
                stages: query,
                selector: x => _mapper.Map<RenderHistoryDto>(x),
                include: x => x.Include(i => i.ChannelYoutube).ThenInclude(o => o.ManagerBOT),
                orderBy: x => x.OrderByDescending(i => i.CreatedTime));

        }

        public async Task<RenderHistoryDto> GetRenderByIdAsync(string userId, int id)
        {
            var _repository = _unitOfWork.GetRepository<RenderHistory>();

            return await _repository.GetFirstOrDefaultAsync(
                predicate: x => x.UserId == userId
                && x.Id == id
                && x.DeletedTime == null,
                selector: x => _mapper.Map<RenderHistoryDto>(x),
                include: x => x.Include(i => i.ChannelYoutube).ThenInclude(o => o.ManagerBOT));
        }

        public async Task<RenderReportClientDto> GetReportRenderAsync(string userId)
        {
            var _repositoryRender = _unitOfWork.GetRepository<RenderHistory>();

            var data = new RenderReportClientDto();

            data.TotalRender = await _repositoryRender.Queryable().AsNoTracking()
                .Where(x => x.UserId == userId).CountAsync();
            data.TotalRenderInRun = await _repositoryRender.Queryable().AsNoTracking()
                .Where(x => x.UserId == userId
                && (x.Status == WorkStatus.Rendering || x.Status == WorkStatus.Downloading)).CountAsync();
            data.TotalRenderUpload = await _repositoryRender.Queryable().AsNoTracking()
                .Where(x => x.UserId == userId && x.Status == WorkStatus.Uploading).CountAsync();
            data.TotalRenderPending = await _repositoryRender.Queryable().AsNoTracking()
                .Where(x => x.UserId == userId
                && (x.Status == WorkStatus.Pending
                || x.Status == WorkStatus.Queueing
                || x.Status == WorkStatus.Schedule)).CountAsync();
            return data;
        }

        public async Task<KeyValuePair<bool, string>> ScheduleRenderAsync()
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<RenderHistory>();

                var timeCurrent = DateTime.Now;

                var datas = await _repository.Queryable().AsNoTracking()
                    .Where(x => x.Status == WorkStatus.Schedule
                    && x.ScheduleTime < timeCurrent).ToListAsync();
                if (datas.Any())
                {
                    foreach (var item in datas)
                    {
                        await StartAsync(item.Id);
                    }
                }
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"ScheduleRenderAsync failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
        }

        public async Task<KeyValuePair<bool, string>> StartAsync(int id)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<RenderHistory>();
                var renderEntity = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.Id == id, disableTracking: false,
                    selector: x => x,
                    include: x => x.Include(i => i.ChannelYoutube).ThenInclude(o => o.ManagerBOT));

                if (renderEntity == null)
                {
                    return new KeyValuePair<bool, string>(false, "Dữ liệu không tồn tại!");
                }
                if (renderEntity.ChannelYoutube.ManagerBOT.Status == ManagerBOTStatus.Disconnected)
                {
                    return new KeyValuePair<bool, string>(false, "BOT chưa kết nối hoặc không hoạt động!");
                }

                //begin send data to bot

                //end send data to bot

                renderEntity.IsError = false;
                renderEntity.ErrorMessage = string.Empty;
                renderEntity.Status = WorkStatus.Queueing;
                // renderEntity.Action = RenderAction.Waiting;
                renderEntity.UpdatedTime = DateTime.Now;
                _repository.Update(renderEntity);
                await _unitOfWork.SaveChangesAsync();

                //send data to BOT
                var result = await SendDataToBotAsync(renderEntity);

                if (!result.Key)
                {
                    return new KeyValuePair<bool, string>(false, result.Value);
                }

                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Start render failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Start không thành công:[{ex.Message}]");
            }
        }

        public async Task<KeyValuePair<bool, string>> StartAsync(string userId, int id)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<RenderHistory>();
                var _repositoryUserChannel = _unitOfWork.GetRepository<UserChannel>();
                var renderEntity = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.Id == id && x.UserId == userId, disableTracking: false,
                    selector: x => x,
                    include: x => x.Include(i => i.ChannelYoutube).ThenInclude(o => o.ManagerBOT));

                if (renderEntity == null)
                {
                    return new KeyValuePair<bool, string>(false, "Dữ liệu không tồn tại!");
                }
                if (renderEntity.ChannelYoutube.ManagerBOT.Status == ManagerBOTStatus.Disconnected)
                {
                    return new KeyValuePair<bool, string>(false, "BOT chưa kết nối hoặc không hoạt động!");
                }
                var anyUserChannel = await _repositoryUserChannel.Queryable().AsNoTracking()
                    .Where(x => x.UserId == userId
                    && x.ChannelYoutubeId == renderEntity.ChannelYoutubeId
                    || x.ChannelYoutube.ManagerBOT.UserIdManager == userId).AnyAsync();
                if (!anyUserChannel)
                {
                    return new KeyValuePair<bool, string>(false, "Bạn không có quyền với Channel này, vui lòng thử lại!");
                }
                //begin send data to bot

                //end send data to bot

                renderEntity.IsError = false;
                renderEntity.ErrorMessage = string.Empty;
                //renderEntity.Status = WorkStatus.Queueing;
                // renderEntity.Action = RenderAction.Waiting;
                renderEntity.UpdatedTime = DateTime.Now;
                _repository.Update(renderEntity);
                await _unitOfWork.SaveChangesAsync();

                //send data to BOT
                var result = await SendDataToBotAsync(renderEntity);

                if (!result.Key)
                {
                    return new KeyValuePair<bool, string>(false, result.Value);
                }

                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Start render failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Start không thành công:[{ex.Message}]");
            }
        }

        public async Task<KeyValuePair<bool, string>> StopAsync(string userId, int id)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<RenderHistory>();
                var renderEntity = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.Id == id && x.UserId == userId, disableTracking: false,
                    selector: x => x,
                    include: x => x.Include(i => i.ChannelYoutube).ThenInclude(o => o.ManagerBOT));

                if (renderEntity == null)
                {
                    return new KeyValuePair<bool, string>(false, "Dữ liệu không tồn tại!");
                }
                //if (renderEntity.ChannelYoutube.ManagerBOT.Status == ManagerBOTStatus.Disconnected)
                //{
                //    return new KeyValuePair<bool, string>(false, "BOT chưa kết nối hoặc không hoạt động!");
                //}

                //begin send data to bot
                await _botContextHub
                    .Clients
                    .Client(renderEntity.ChannelYoutube.ManagerBOT.ConnectionId)
                    .CancelWorkAsync(new Identy
                    {
                        ItemId = renderEntity.Id
                    });
                //end send data to bot

                //renderEntity.Action = RenderAction.Cancel;
                renderEntity.UpdatedTime = DateTime.Now;
                renderEntity.Status = WorkStatus.Cancelled;
                _repository.Update(renderEntity);
                await _unitOfWork.SaveChangesAsync();
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Start render failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Start không thành công:[{ex.Message}]");
            }
        }

        public async Task<KeyValuePair<bool, string>> UpdateAsync(string userId, int id, RenderUpdateDto model)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<RenderHistory>();

                var renderEntity = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.Id == id && x.UserId == userId, disableTracking: true);

                if (renderEntity == null)
                {
                    return new KeyValuePair<bool, string>(false, "Dữ liệu không tồn tại!");
                }

                renderEntity.ChannelYoutubeId = model.ChannelId;
                renderEntity.AudioLoop = model.AudioLoop;
                renderEntity.Intro = model.Intro;
                renderEntity.Outtro = model.Outtro;
                renderEntity.VideoLoop = model.VideoLoop;
                renderEntity.VideoName = model.VideoName;
                renderEntity.UpdatedTime = DateTime.Now;

                _repository.Update(renderEntity);

                await _unitOfWork.SaveChangesAsync();
                return new KeyValuePair<bool, string>(true, string.Empty);

            }
            catch (Exception ex)
            {
                _logger.LogError($"Clone Render [{id}] failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Clone Render không thành công:[{ex.Message}]");
            }
        }

        public Task<KeyValuePair<bool, string>> ValidateLinkAsync(string link)
        {
            return _validateLinkService.ValidateLinkAsync(link);
        }


        private async Task<KeyValuePair<bool, string>> SendDataToBotAsync(RenderHistory model)
        {
            try
            {
                var data = new WorkData();

                data.DurationOutput = model.TimeRender;
                data.ItemId = model.Id;
                data.ProfileId = model.ChannelYoutube.ProfileId;
                data.FileDatas = new List<FileData>();
                data.UploadTitleName = model.VideoName;
                data.ScheduleTime = model.ScheduleTime;
                //video intro
                if (!string.IsNullOrWhiteSpace(model.Intro))
                {
                    var urlType = _validateLinkService.GetUrlType(model.Intro);
                    if (!urlType.HasValue)
                        return new KeyValuePair<bool, string>(false, $"Url không hỗ trợ {model.Intro}");
                    data.FileDatas.Add(new FileData
                    {
                        Name = "videoIntro",
                        Url = model.Intro,
                        UrlType = urlType.Value,
                        FilePosition = FilePosition.Intro,
                        FileType = FileType.Video
                    });
                }

                //video loop
                if (!string.IsNullOrWhiteSpace(model.VideoLoop))
                {
                    var urlType = _validateLinkService.GetUrlType(model.VideoLoop);
                    if (!urlType.HasValue)
                        return new KeyValuePair<bool, string>(false, $"Url không hỗ trợ {model.VideoLoop}");
                    data.FileDatas.Add(new FileData
                    {
                        Name = "videoLoop",
                        Url = model.VideoLoop,
                        UrlType = urlType.Value,
                        FilePosition = FilePosition.Loop,
                        FileType = FileType.Video
                    });
                }

                //audio loop
                if (!string.IsNullOrWhiteSpace(model.AudioLoop))
                {
                    var urlType = _validateLinkService.GetUrlType(model.AudioLoop);
                    if (!urlType.HasValue)
                        return new KeyValuePair<bool, string>(false, $"Url không hỗ trợ {model.AudioLoop}");
                    data.FileDatas.Add(new FileData
                    {
                        Name = "audioLoop",
                        Url = model.AudioLoop,
                        UrlType = urlType.Value,
                        FilePosition = FilePosition.Loop,
                        FileType = FileType.Audio
                    });
                }

                //outro
                if (!string.IsNullOrWhiteSpace(model.Outtro))
                {
                    var urlType = _validateLinkService.GetUrlType(model.Outtro);
                    if (!urlType.HasValue)
                        return new KeyValuePair<bool, string>(false, $"Url không hỗ trợ {model.Outtro}");
                    data.FileDatas.Add(new FileData
                    {
                        Name = "audioOutro",
                        Url = model.Outtro,
                        UrlType = urlType.Value,
                        FilePosition = FilePosition.Outro,
                        FileType = FileType.Audio
                    });
                }

                await _botContextHub
                     .Clients
                     .Client(model.ChannelYoutube.ManagerBOT.ConnectionId)
                     .PushWorkAsync(data);

                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"SendDataToBot failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"SendData lỗi:[{ex.Message}]");
            }
        }
    }
}
