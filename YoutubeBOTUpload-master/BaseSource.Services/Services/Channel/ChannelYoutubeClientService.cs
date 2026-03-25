using AutoMapper;
using BaseSource.Data.EF;
using BaseSource.Data.Entities;
using BaseSource.Shared.Enums;
using BaseSource.ViewModels.Channel;
using EFCore.UnitOfWork;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace BaseSource.Services.Services.Channel
{
    public class ChannelYoutubeClientService : IChannelYoutubeClientService
    {
        private readonly IUnitOfWork _unitOfWork;
        private readonly ILogger<ChannelYoutubeClientService> _logger;
        private readonly IMapper _mapper;
        public ChannelYoutubeClientService(
            IUnitOfWork<BaseSourceDbContext> unitOfWork,
            ILogger<ChannelYoutubeClientService> logger,
            IMapper mapper
            )
        {
            _unitOfWork = unitOfWork;
            _logger = logger;
            _mapper = mapper;
        }

        public async Task<KeyValuePair<bool, string>> AddChannelToUserAsync(AddUserChannelDto model)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<UserChannel>();

                var isAny = await _repository.ExistsAsync(x => x.ChannelYoutubeId == model.ChannelYoutubeId
                && x.UserId == model.UserId);
                if (!isAny)
                {
                    _repository.Insert(new UserChannel
                    {
                        UserId = model.UserId,
                        CreatedTime = DateTime.Now,
                        ChannelYoutubeId = model.ChannelYoutubeId,
                        Status = 1
                    });
                    await _unitOfWork.SaveChangesAsync();
                }
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Add Channel to User failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Cập nhật không thành công:[{ex.Message}]");
            }
        }

        public async Task<List<ChannelYoutubeDto>> GetChannelByUser(string userId)
        {
            var _repository = _unitOfWork.GetRepository<UserChannel>();
            var _repositoryUser = _unitOfWork.GetRepository<AppUser>();

            var userCurrent = await _repositoryUser.GetFirstOrDefaultAsync(
                predicate: x => x.Id == userId,
                include: x => x.Include(i => i.UserRoles).ThenInclude(o => o.Role));


            if (userCurrent.UserRoles.Any(x => x.Role.Name == "Admin"))
            {
                return await _repository.Queryable().AsNoTracking()
                .Where(x => x.ChannelYoutube.ManagerBOT.DeletedTime == null)
                .Include(x => x.ChannelYoutube).ThenInclude(o => o.ManagerBOT)
                .Select(x => new ChannelYoutubeDto
                {
                    Avatar = x.ChannelYoutube.Avatar,
                    ChannelYTId = x.ChannelYoutube.ChannelYTId,
                    Name = x.ChannelYoutube.Name,
                    BotName = x.ChannelYoutube.ManagerBOT.Name,
                    BotGroup = x.ChannelYoutube.ManagerBOT.Group,
                    Id = x.ChannelYoutubeId,
                    Status = x.ChannelYoutube.ManagerBOT.Status,

                }).ToListAsync();
            }
            if (userCurrent.UserRoles.Any(x => x.Role.Name == "Manager"))
            {
                return await _repository.Queryable().AsNoTracking()
                .Where(x => x.ChannelYoutube.ManagerBOT.DeletedTime == null
                && x.ChannelYoutube.ManagerBOT.UserIdManager == userId)
                .Include(x => x.ChannelYoutube).ThenInclude(o => o.ManagerBOT)
                .Select(x => new ChannelYoutubeDto
                {
                    Avatar = x.ChannelYoutube.Avatar,
                    ChannelYTId = x.ChannelYoutube.ChannelYTId,
                    Name = x.ChannelYoutube.Name,
                    BotName = x.ChannelYoutube.ManagerBOT.Name,
                    BotGroup = x.ChannelYoutube.ManagerBOT.Group,
                    Id = x.ChannelYoutubeId,
                    Status = x.ChannelYoutube.ManagerBOT.Status,

                }).ToListAsync();
            }

            return await _repository.Queryable().AsNoTracking()
                .Where(x => x.UserId == userId
                && x.ChannelYoutube.ManagerBOT.UserIdManager == userCurrent.UserIdManager
                //&& x.ChannelYoutube.ManagerBOT.Status == ManagerBOTStatus.Connected
                && x.ChannelYoutube.ManagerBOT.DeletedTime == null)
                .Include(x => x.ChannelYoutube).ThenInclude(o => o.ManagerBOT)
                .Select(x => new ChannelYoutubeDto
                {
                    Avatar = x.ChannelYoutube.Avatar,
                    ChannelYTId = x.ChannelYoutube.ChannelYTId,
                    Name = x.ChannelYoutube.Name,
                    BotName = x.ChannelYoutube.ManagerBOT.Name,
                    BotGroup = x.ChannelYoutube.ManagerBOT.Group,
                    Id = x.ChannelYoutubeId,
                    Status = x.ChannelYoutube.ManagerBOT.Status,

                }).ToListAsync();
        }
    }
}
