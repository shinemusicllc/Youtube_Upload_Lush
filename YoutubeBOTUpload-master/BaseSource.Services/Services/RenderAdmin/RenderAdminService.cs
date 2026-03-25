using AutoMapper;
using BaseSource.Data.EF;
using BaseSource.Data.Entities;
using BaseSource.Services.Services.Signalr;
using BaseSource.SharedSignalrData.Classes;
using BaseSource.SharedSignalrData.Enums;
using BaseSource.ViewModels.Render;
using BaseSource.ViewModels.RenderAdmin;
using EFCore.UnitOfWork;
using EFCore.UnitOfWork.PageList;
using Microsoft.AspNetCore.SignalR;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using BaseSource.SharedSignalrData.Interfaces;

namespace BaseSource.Services.Services.RenderAdmin
{
    public class RenderAdminService : IRenderAdminService
    {
        private readonly IUnitOfWork _unitOfWork;
        private readonly ILogger<RenderAdminService> _logger;
        private readonly IMapper _mapper;
        private readonly IHubContext<BotHub, IClientHub> _botContextHub;
        private readonly IHubContext<WebHub, IWebClientHub> _clientContextHub;
        public RenderAdminService(
            IUnitOfWork<BaseSourceDbContext> unitOfWork,
            ILogger<RenderAdminService> logger,
            IMapper mapper
            , IHubContext<BotHub, IClientHub> botContextHub
            , IHubContext<WebHub, IWebClientHub> clientContextHub
            )
        {
            _unitOfWork = unitOfWork;
            _logger = logger;
            _mapper = mapper;
            _botContextHub = botContextHub;
            _clientContextHub = clientContextHub;
        }

        public async Task<KeyValuePair<bool, string>> DeleteAsync(string username)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<RenderHistory>();
                var _repositoryConfig = _unitOfWork.GetRepository<ConfigSystem>();

                var renders = await _repository.Queryable()
                    .Where(x => x.Status == WorkStatus.Cancelled
                    || x.Status == WorkStatus.Completed
                    || x.Status == WorkStatus.Error).ToListAsync();
                if (renders.Any())
                {
                    _repository.Delete(renders);
                    var config = await _repositoryConfig.GetFirstOrDefaultAsync(disableTracking: false);
                    if (config != null)
                    {
                        config.UserDeleteChannel = username;
                        config.DeletedTimeChannel = DateTime.Now;
                        _repositoryConfig.Update(config);
                    }
                    await _unitOfWork.SaveChangesAsync();
                }
                return new KeyValuePair<bool, string>(true, string.Empty);

            }
            catch (Exception ex)
            {
                _logger.LogError($"Delete Render failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Xóa dữ liệu không thành công:[{ex.Message}]");
            }
        }

        public async Task<IPagedList<RenderAdminInfoDto>> GetAllAsync(RenderAdminRequestDto model, string userId, bool isAdmin = false)
        {
            var _repository = _unitOfWork.GetRepository<RenderHistory>();

            var query = _repository.Queryable().AsNoTracking();
            if (!isAdmin)
            {
                query = query.Where(x => x.AppUser.UserIdManager == userId || x.UserId == userId);
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
                    query = query.Where(x => lstManagers.Any(i => i == x.AppUser.UserIdManager) || lstManagers.Any(i => i == x.UserId));
                }
            }
            return await _repository.GetStagesPagedListAsync(
                stages: query,
                selector: x => new RenderAdminInfoDto
                {
                    BotName = x.ChannelYoutube.ManagerBOT.Name,
                    Group = x.ChannelYoutube.ManagerBOT.Group,
                    Gmail = x.ChannelYoutube.Gmail,
                    ChannelName = x.ChannelYoutube.Name,
                    ChannelId = x.ChannelYoutubeId,
                    ChannelYTId = x.ChannelYoutube.ChannelYTId,
                    VideoLink = x.VideoLink,
                    Status = x.Status,
                    // Action = x.Action,
                    IsError = x.IsError,
                    ErrorMessage = x.ErrorMessage,
                    UserId = x.UserId,
                    UserName = x.AppUser.UserName,
                    CreatedTime = x.CreatedTime,
                    Id = x.Id,
                    DownloadStartTime = x.DownloadStartTime,
                    Pencent = x.Pencent,
                    RenderStartTime = x.RenderStartTime,
                    UploadStartTime = x.UploadStartTime,
                    UploadTimeCompleted = x.UploadTimeCompleted,
                    VideoName = x.VideoName,
                    Avatar = x.ChannelYoutube.Avatar,
                    //TimeRender = x.TimeRender,
                    TimeRenderLong = x.TimeRenderLong,
                    Order = x.Order,
                    ScheduleTime = x.ScheduleTime,
                    UserIdManager = x.AppUser.UserIdManager,
                    UserManager = x.AppUser.Manager.UserName ,
                }, include: x => x.Include(i => i.AppUser).ThenInclude(o => o.Manager).Include(i => i.ChannelYoutube).ThenInclude(o => o.ManagerBOT),
                orderBy: x => x.OrderByDescending(i => i.CreatedTime),
                pageIndex: model.Page, pageSize: model.PageSize);
        }

        public async Task<List<RenderAdminInfoDto>> GetAllByChannelAsync(int channelId)
        {
            var _repository = _unitOfWork.GetRepository<RenderHistory>();
            return await _repository.Queryable()
                .Where(x => x.ChannelYoutubeId == channelId)
                .Include(x => x.AppUser).Include(x => x.ChannelYoutube).ThenInclude(o => o.ManagerBOT)
                .Select(x => new RenderAdminInfoDto
                {
                    BotName = x.ChannelYoutube.ManagerBOT.Name,
                    Group = x.ChannelYoutube.ManagerBOT.Group,
                    Gmail = x.ChannelYoutube.Gmail,
                    ChannelName = x.ChannelYoutube.Name,
                    ChannelId = x.ChannelYoutubeId,
                    ChannelYTId = x.ChannelYoutube.ChannelYTId,
                    VideoLink = x.VideoLink,
                    Status = x.Status,
                    // Action = x.Action,
                    IsError = x.IsError,
                    ErrorMessage = x.ErrorMessage,
                    UserId = x.UserId,
                    UserName = x.AppUser.UserName,
                    CreatedTime = x.CreatedTime,
                    Id = x.Id,
                    DownloadStartTime = x.DownloadStartTime,
                    Pencent = x.Pencent,
                    RenderStartTime = x.RenderStartTime,
                    UploadStartTime = x.UploadStartTime,
                    UploadTimeCompleted = x.UploadTimeCompleted,
                    VideoName = x.VideoName,
                    Avatar = x.ChannelYoutube.Avatar,
                    //TimeRender = x.TimeRender,
                    TimeRenderLong = x.TimeRenderLong,
                    Order = x.Order,
                    ScheduleTime = x.ScheduleTime
                }).OrderByDescending(x => x.CreatedTime).ToListAsync();
        }

        public async Task<RenderHistoryDto> GetByIdAsync(int id)
        {
            var _repository = _unitOfWork.GetRepository<RenderHistory>();

            return await _repository.GetFirstOrDefaultAsync(
                predicate: x => x.Id == id && x.DeletedTime == null,
                selector: x => _mapper.Map<RenderHistoryDto>(x),
                include: x => x.Include(i => i.ChannelYoutube).ThenInclude(o => o.ManagerBOT));
        }

        public async Task<KeyValuePair<bool, string>> WorkUpdateAsync(WorkResponse model)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<RenderHistory>();

                var renderEntity = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.Id == model.ItemId, disableTracking: false);
                if (renderEntity != null)
                {
                    renderEntity.UpdatedTime = DateTime.Now;
                    renderEntity.Status = model.WorkStatus;
                    renderEntity.IsError = model.WorkStatus == WorkStatus.Error;
                    renderEntity.ErrorMessage = model.Message;
                    renderEntity.UpdatedTime = DateTime.Now;
                    renderEntity.VideoLink = model.VideoUploadedUrl;
                    renderEntity.UploadStartTime = model.TimeStartUpload;
                    renderEntity.UploadTimeCompleted = model.TimeCompleted;
                    renderEntity.DownloadStartTime = model.TimeStartDownload;
                    renderEntity.RenderStartTime = model.TimeStartRender;
                    // renderEntity.Status = RenderStatus.Render;
                    renderEntity.Pencent = (model.Percentage * 100);
                    renderEntity.Order = model.QueueIndex ?? 0;
                    if (renderEntity.Status == WorkStatus.Cancelled
                        || renderEntity.Status == WorkStatus.Error
                        || renderEntity.Status == WorkStatus.Completed)
                    {
                        renderEntity.Order = 0;
                    }

                    _repository.Update(renderEntity);
                    await _unitOfWork.SaveChangesAsync();


                    await _clientContextHub.Clients.All.RenderInfo(_mapper.Map<RenderHistoryDto>(renderEntity));
                }
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {

                _logger.LogError($"WorkUpdate failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"WorkUpdate lỗi[{ex.Message}]");
            }
        }
    }
}
