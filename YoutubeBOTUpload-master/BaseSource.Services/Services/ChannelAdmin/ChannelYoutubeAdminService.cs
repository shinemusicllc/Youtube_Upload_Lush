using AutoMapper;
using BaseSource.Data.EF;
using BaseSource.Data.Entities;
using BaseSource.Services.Services.Signalr;
using BaseSource.SharedSignalrData.Classes;
using BaseSource.SharedSignalrData.Interfaces;
using BaseSource.ViewModels.ChannelAdmin;
using EFCore.UnitOfWork;
using EFCore.UnitOfWork.PageList;
using Microsoft.AspNetCore.SignalR;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace BaseSource.Services.Services.ChannelAdmin
{
    public class ChannelYoutubeAdminService : IChannelYoutubeAdminService
    {
        private readonly IUnitOfWork _unitOfWork;
        private readonly ILogger<ChannelYoutubeAdminService> _logger;
        private readonly IMapper _mapper;
        private readonly IHubContext<BotHub, IClientHub> _botContextHub;

        public ChannelYoutubeAdminService(
            IUnitOfWork<BaseSourceDbContext> unitOfWork,
            ILogger<ChannelYoutubeAdminService> logger,
            IMapper mapper,
            IHubContext<BotHub, IClientHub> botContextHub
            )
        {
            _unitOfWork = unitOfWork;
            _logger = logger;
            _mapper = mapper;
            _botContextHub = botContextHub;
        }

        public async Task<KeyValuePair<bool, string>> ChromeProfileUpdateAsync(string botId, List<ChromeProfileData> model)
        {
            try
            {
                //_logger.LogInformation($"Begin ChromeProfileUpdateAsync");
                // _logger.LogInformation($"Total Profile:[{model.Count}]");
                var _repository = _unitOfWork.GetRepository<ChannelYoutube>();
                var _repositoryBot = _unitOfWork.GetRepository<ManagerBOT>();

                var botCurrent = await _repositoryBot.GetFirstOrDefaultAsync(
                    predicate: x => x.BotId == botId, disableTracking: false);
                if (botCurrent != null)
                {
                    var channelOlds = await _repository.Queryable()
                    .Where(x => x.ManagerBOT.BotId == botId).ToListAsync();

                    var channelInserts = new List<ChannelYoutube>();

                    foreach (var item in model)
                    {
                        var channelCurrent = channelOlds.Where(x => x.ProfileId == item.ProfileId).FirstOrDefault();
                        if (channelCurrent != null)
                        {
                            channelCurrent.Avatar = item.AvatarUrl;
                            channelCurrent.UpdatedTime = DateTime.Now;
                            channelCurrent.Name = item.ChannelName;
                            channelCurrent.Gmail = item.Email;
                            channelCurrent.ChannelYTId = item.ChannelId;
                            _repository.Update(channelCurrent);
                        }
                        else
                        {
                            channelInserts.Add(new ChannelYoutube
                            {
                                ChannelYTId = item.ChannelId,
                                Name = item.ChannelName,
                                ProfileId = item.ProfileId,
                                Avatar = item.AvatarUrl,
                                Gmail = item.Email,
                                CreatedTime = DateTime.Now,
                                ManagerBOTId = botCurrent.Id
                            });
                        }
                    }
                    if (channelInserts != null && channelInserts.Any())
                    {
                        _repository.Insert(channelInserts);
                    }

                    // channel removes1

                    var channelRemoves = channelOlds.Where(x => !model.Any(i => i.ProfileId == x.ProfileId)).ToList();

                    if (channelRemoves.Any())
                    {
                        _repository.Delete(channelRemoves);
                    }

                    await _unitOfWork.SaveChangesAsync();
                    // _logger.LogInformation($"End ChromeProfileUpdateAsync");
                }


                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Update Chorm Profile failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Cập nhật lỗi:[{ex.Message}]");
            }
        }

        public async Task<KeyValuePair<bool, string>> DeleteAsync(int id)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<ChannelYoutube>();
                var channelEntity = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.Id == id, disableTracking: false,
                    include: x => x.Include(i=>i.ManagerBOT).Include(i => i.UserChannels).Include(i => i.RenderHistorys));
                if (channelEntity != null)
                {
                    var channelClone = channelEntity;
                    _repository.Delete(channelEntity);
                    await _unitOfWork.SaveChangesAsync();

                    await _botContextHub.Clients.Client(channelClone.ManagerBOT.ConnectionId).DeleteProfilesAsync(new List<string> { channelClone.ProfileId });
                }
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Delete channel [{id}] failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, ex.Message);
            }
        }

        public async Task<IPagedList<ChannelAdminDto>> GetAllAsync(ChannelAdminRequestDto model, string userId, bool isAdmin)
        {
            var _repository = _unitOfWork.GetRepository<ChannelYoutube>();
            var query = _repository.Queryable();
            if (!isAdmin)
            {
                query = query.Where(x => x.ManagerBOT.UserIdManager == userId);
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
                    query = query.Where(x => lstManagers.Any(i => i == x.ManagerBOT.UserIdManager));
                }
            }
            return await _repository.GetStagesPagedListAsync(
                stages: query,
                selector: x => new ChannelAdminDto
                {
                    BotName = x.ManagerBOT.Name,
                    ChannelGmail = x.Gmail,
                    ChannelYTId = x.ChannelYTId,
                    ChannelName = x.Name,
                    Group = x.ManagerBOT.Group,
                    CreatedTime = DateTime.Now,
                    Id = x.Id,
                    Status = x.ManagerBOT.Status,
                    Avatar = x.Avatar,
                    TotalUser = x.UserChannels.Select(x => x.UserId).Distinct().Count(),
                    UserIdManager = x.ManagerBOT.UserIdManager,
                    UserManager = x.ManagerBOT.User.UserName,
                    UserJoins = x.UserChannels.Select(i => i.AppUser.UserName).ToList()
                },
                include: x => x.Include(i => i.ManagerBOT).Include(i => i.UserChannels),
                pageIndex: model.Page, pageSize: model.PageSize);
        }

        public async Task<List<ChannelAdminDto>> GetAllByUserIdAsync(string userId, bool isAdmin = false)
        {
            var _repository = _unitOfWork.GetRepository<ChannelYoutube>();
            var _repositoryUser = _unitOfWork.GetRepository<AppUser>();

            var userCurrent = await _repositoryUser.GetFirstOrDefaultAsync(
                predicate: x => x.Id == userId);

            var query = _repository.Queryable();
            if (!isAdmin)
            {
                query = query.Where(x => x.ManagerBOT.UserIdManager == userCurrent.UserIdManager || x.ManagerBOT.UserIdManager == userId);
            }
            return await query.Where(x => x.DeletedTime == null)
                .Include(x => x.ManagerBOT).Include(i => i.UserChannels)
                .Select(x => new ChannelAdminDto
                {
                    BotName = x.ManagerBOT.Name,
                    ChannelGmail = x.Gmail,
                    ChannelYTId = x.ChannelYTId,
                    ChannelName = x.Name,
                    Group = x.ManagerBOT.Group,
                    CreatedTime = DateTime.Now,
                    Id = x.Id,
                    Status = x.ManagerBOT.Status,
                    TotalUser = x.UserChannels.Select(x => x.UserId).Distinct().Count(),
                    IsUsed = x.UserChannels.Any(i => i.UserId == userId),
                    Avatar = x.Avatar
                }).ToListAsync();
        }

        public async Task<List<ChannelAdminDto>> GetAllReportAsync()
        {
            var _repository = _unitOfWork.GetRepository<ChannelYoutube>();
            var query = _repository.Queryable();

            return await query.Where(x => x.DeletedTime == null)
                .Include(x => x.ManagerBOT).Include(i => i.UserChannels)
                .Select(x => new ChannelAdminDto
                {
                    BotName = x.ManagerBOT.Name,
                    ChannelGmail = x.Gmail,
                    ChannelYTId = x.ChannelYTId,
                    ChannelName = x.Name,
                    Group = x.ManagerBOT.Group,
                    CreatedTime = DateTime.Now,
                    Id = x.Id,
                    Status = x.ManagerBOT.Status,
                    TotalUser = x.UserChannels.Select(x => x.UserId).Distinct().Count(),
                    Avatar = x.Avatar,
                    UserManager = x.ManagerBOT.User.UserName,
                    UserJoins = x.UserChannels.Select(i => i.AppUser.UserName).ToList(),
                }).ToListAsync();
        }

        public async Task<ChannelAdminDto> GetByIdAsync(int id)
        {
            throw new NotImplementedException();
        }

        public async Task<List<ChannelAdminDto>> GetChannelByBotIdAsync(int botId)
        {
            var _repository = _unitOfWork.GetRepository<ChannelYoutube>();
            var query = _repository.Queryable();

            return await query.Where(x => x.ManagerBOTId == botId)
                .Include(x => x.ManagerBOT).Include(i => i.UserChannels)
                .Select(x => new ChannelAdminDto
                {
                    BotName = x.ManagerBOT.Name,
                    ChannelGmail = x.Gmail,
                    ChannelYTId = x.ChannelYTId,
                    ChannelName = x.Name,
                    Group = x.ManagerBOT.Group,
                    CreatedTime = DateTime.Now,
                    Id = x.Id,
                    TotalUser = x.UserChannels.Select(x => x.UserId).Distinct().Count(),
                    Avatar = x.Avatar
                }).ToListAsync();
        }

        public async Task<List<UserChannelAdminInfoDto>> GetUserOfChannelIdAsync(int channelId)
        {
            var _repository = _unitOfWork.GetRepository<AppUser>();
            return await _repository.Queryable().AsNoTracking()
                .Where(x => x.UserChannels.Any(i => i.ChannelYoutubeId == channelId))
                .Select(x => new UserChannelAdminInfoDto
                {
                    Password = x.Password,
                    UserId = x.Id,
                    UserName = x.UserName,
                    TotalChannel = x.UserChannels.Count(),
                    TotalBot = x.UserChannels.Select(i => i.ChannelYoutube.ManagerBOTId).Distinct().Count()
                }).ToListAsync();
        }

        public async Task<KeyValuePair<bool, string>> UpdateChannelOfUser(UpdateUserChannelDto model)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<UserChannel>();

                var entity = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.ChannelYoutubeId == model.ChannelId
                    && x.UserId == model.UserId,
                    disableTracking: false);

                if (entity != null)
                {
                    _repository.Delete(entity);
                }
                else
                {
                    _repository.Insert(new UserChannel
                    {
                        CreatedTime = DateTime.Now,
                        ChannelYoutubeId = model.ChannelId,
                        UserId = model.UserId,
                        Status = 1
                    });
                }
                await _unitOfWork.SaveChangesAsync();
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Update UserChannel failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Cập nhật không thành công[{ex.Message}]");
            }
        }

        public async Task<KeyValuePair<bool, string>> UpdateProfileAsync(int channelId)
        {
            var _repository = _unitOfWork.GetRepository<ChannelYoutube>();
            var channelEntity = await _repository.GetFirstOrDefaultAsync(
                predicate: x => x.Id == channelId,
                include: x => x.Include(i => i.ManagerBOT));
            if (channelEntity != null)
            {
                await _botContextHub.Clients.Client(channelEntity.ManagerBOT.ConnectionId).GetInfoChannelAsync(channelEntity.ProfileId);
            }
            return new KeyValuePair<bool, string>(true, string.Empty);
        }
    }
}