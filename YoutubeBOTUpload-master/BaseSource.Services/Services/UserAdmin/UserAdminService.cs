
using BaseSource.Shared.Enums;
using BaseSource.Shared.Helpers;
using BaseSource.Data.EF;
using BaseSource.Data.Entities;
using BaseSource.ViewModels.UserAdmin;
using EFCore.UnitOfWork;
using EFCore.UnitOfWork.PageList;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Microsoft.AspNetCore.SignalR;
using BaseSource.Services.Services.Signalr;
using BaseSource.SharedSignalrData.Interfaces;
using BaseSource.SharedSignalrData.Classes;

namespace BaseSource.Services.Services.UserAdmin
{
    public class UserAdminService : IUserAdminService
    {
        private readonly IUnitOfWork _unitOfWork;
        private readonly RoleManager<AppRole> _roleManager;
        private readonly ILogger<UserAdminService> _logger;
        private readonly IHubContext<BotHub, IClientHub> _botContextHub;
        public UserAdminService(IUnitOfWork<BaseSourceDbContext> unitOfWork,
             RoleManager<AppRole> roleManager, ILogger<UserAdminService> logger
            , IHubContext<BotHub, IClientHub> botContextHub
            )
        {
            _unitOfWork = unitOfWork;
            _roleManager = roleManager;
            _logger = logger;
            _botContextHub = botContextHub;


        }

        public async Task<KeyValuePair<bool, string>> CreateUserAsync(UserCreateAdminDto model)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<AppUser>();

                var existUser = await _repository.ExistsAsync(x => x.UserName.ToLower() == model.UserName.ToLower());
                if (existUser)
                {
                    return new KeyValuePair<bool, string>(false, "Tài khoản đã tồn tại!");
                }


                var userIdParent = string.Empty;

                var hasher = new PasswordHasher<AppUser>();

                var user = new AppUser
                {
                    Email = model.UserName,
                    UserName = model.UserName,
                    SecurityStamp = Guid.NewGuid().ToString(),
                    PhoneNumber = "123456789",
                    PasswordHash = hasher.HashPassword(null, model.Password),
                    Password = model.Password,
                    CreatedTime = DateTime.Now,
                    NormalizedEmail = model.UserName,
                    NormalizedUserName = model.UserName,
                    UserIdManager = string.IsNullOrWhiteSpace(model.UserIdManager) ? null : model.UserIdManager,
                    //LinkFB = string.Empty,
                    //TelegramAPI = model.LinkTelegram,
                    //NumberOfThreads1080 = model.NumberOfThreads1080,
                    //NumberOfThreads4K = model.NumberOfThreads4K

                };
                await _unitOfWork.GetRepository<AppUser>().InsertAsync(user);
                await _unitOfWork.SaveChangesAsync();

                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Create account failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(true, "Create account failed");
            }
        }


        public async Task<KeyValuePair<bool, string>> DeleteAsync(string userId)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<AppUser>();
                var _repositoryUserChannel = _unitOfWork.GetRepository<UserChannel>();

                var _repositoryRender = _unitOfWork.GetRepository<RenderHistory>();

                // var _repositoryUserBOT = _unitOfWork.GetRepository<UserManagerBOT>();

                var userCurrent = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.Id == userId, disableTracking: false);
                if (userCurrent == null)
                {
                    return new KeyValuePair<bool, string>(false, "Người dùng không tồn tại!");
                }
                userCurrent.DeletedTime = DateTime.Now;
                //remove usermanagerBot

                var userChannels = await _repositoryUserChannel.Queryable().Where(x => x.UserId == userId).ToListAsync();
                if (userChannels.Any())
                {
                    _repositoryUserChannel.Delete(userChannels);
                }
                var renders = await _repositoryRender.Queryable()
                    .Where(x => x.UserId == userId
                    //&& x.Status == RenderStatus.Render
                    ).ToListAsync();
                if (renders.Any())
                {
                    foreach (var item in renders)
                    {
                        //cancel renders
                        //await renders.CancelStreamAsync(userId, item.Id);
                    }
                }

                // userCurrent.UserManagerBOTs = null;
                //userCurrent.NumberOfThreads4K = 0;
                //userCurrent.UserManagerBOTs = null;
                _repository.Update(userCurrent);

                await _unitOfWork.SaveChangesAsync();
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Delete User failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Xóa người dùng không thành công:[{ex.Message}]");
            }
        }



        public async Task<List<UserGroupDto>> GetAllUserOfManagerAsync(string userId)
        {
            var _repository = _unitOfWork.GetRepository<AppUser>();

            var query = _repository.Queryable().AsNoTracking();


            return await _repository.Queryable().AsNoTracking()
                .Select(x => new UserGroupDto
                {
                    UserId = x.Id,
                    UserManagerId = userId,
                    UserName = x.UserName
                }).ToListAsync();


        }

        public async Task<List<UserAdminInfoDto>> GetUserAdminAsync()
        {
            var _repository = _unitOfWork.GetRepository<AppUser>();
            var roleManager = await _roleManager.FindByNameAsync("Admin");

            var query = _repository.Queryable().AsNoTracking();

            query = query.Where(x => x.DeletedTime == null &&
            x.UserRoles.Any(i => i.RoleId == roleManager.Id));

            var data = await _repository.GetStagesPagedListAsync(
                stages: query,
                selector: x => new UserAdminInfoDto
                {
                    CreatedTime = x.CreatedTime,
                    Email = x.Email,
                    Id = x.Id,
                    LinkFB = x.LinkFB,
                    LinkTelegram = x.LinkTelegram,

                    UserName = x.UserName,
                    TelegramAPI = x.TelegramAPI
                },
                orderBy: x => x.OrderByDescending(i => i.CreatedTime),
                pageIndex: 1, pageSize: 1000);
            return data.Items.ToList();
        }

        public async Task<List<UserManagerBotInfoDto>> GetUserBotAsync(string userId)
        {
            //var _repository = _unitOfWork.GetRepository<UserManagerBOT>();

            //return await _repository.Queryable().AsNoTracking()
            //    .Where(x => x.UserId == userId)
            //    .Include(x => x.ManagerBOT).ThenInclude(i => i.StreamHistorys)
            //    .Select(x => new UserManagerBotInfoDto
            //    {
            //        Id = x.Id,
            //        BotName = x.ManagerBOT.Name,
            //        NumberOfThreads = x.NumberOfThreads,
            //        UserName = x.User.UserName,
            //        LiveType = x.LiveType,
            //        NumberOfThreadsInRun = x.ManagerBOT.StreamHistorys.Where(x => x.UserId == userId && x.Status == StreamStatus.Streaming).Count()
            //    }).ToListAsync();
            return null;
        }



        public async Task<IPagedList<UserAdminInfoDto>> GetUserByFilterAsync(UserAdminRequestDto model, string userId, bool isAdmin = false)
        {
            var _repository = _unitOfWork.GetRepository<AppUser>();

            var query = _repository.Queryable().AsNoTracking();
            query = query.Where(x => x.DeletedTime == null);
            if (!string.IsNullOrEmpty(model.UserName))
            {
                query = query.Where(x => x.UserName.Contains(model.UserName) || x.Email.Contains(model.UserName));
            }
            if (!isAdmin)
            {
                query = query.Where(x => x.UserIdManager == userId || x.Id == userId);
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

            return await _repository.GetStagesPagedListAsync(
                stages: query,
                selector: x => new UserAdminInfoDto
                {
                    CreatedTime = x.CreatedTime,
                    Email = x.Email,
                    Id = x.Id,
                    LinkFB = x.LinkFB,
                    LinkTelegram = x.LinkTelegram,
                    Password = x.Password,
                    //TotalChannel=x
                    UpdatedTime = x.UpdatedTime,
                    UserUpdate = x.UserUpdate,
                    UserName = x.UserName,
                    TotalChannel = x.UserChannels.Count(),
                    TotalBOT = x.UserChannels.Select(i => i.ChannelYoutube.ManagerBOTId).Distinct().Count(),
                    UserIdManager = x.UserIdManager,
                    UserManager = x.Manager.UserName,
                    Roles = x.UserRoles.Select(o => o.Role.Name).ToList()
                },
                include: x => x.Include(i => i.UserChannels),
                orderBy: x => x.OrderByDescending(i => i.CreatedTime),
                pageIndex: model.Page, pageSize: model.PageSize);
        }

        public async Task<List<UserAdminInfoDto>> GetUserManagerAsync()
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<AppUser>();
                var roleManager = await _roleManager.FindByNameAsync("Manager");

                var query = _repository.Queryable().AsNoTracking();

                query = query.Where(x => x.DeletedTime == null &&
                x.UserRoles.Any(i => i.RoleId == roleManager.Id));

                var data = await _repository.GetStagesPagedListAsync(
                    stages: query,
                    selector: x => new UserAdminInfoDto
                    {
                        CreatedTime = x.CreatedTime,
                        Email = x.Email,
                        Id = x.Id,
                        LinkFB = x.LinkFB,
                        LinkTelegram = x.LinkTelegram,

                        UserName = x.UserName,
                        TelegramAPI = x.TelegramAPI
                    },
                    orderBy: x => x.OrderByDescending(i => i.CreatedTime),
                    pageIndex: 1, pageSize: 1000);
                return data.Items.ToList();
            }
            catch (Exception ex)
            {

                throw;
            }

        }

        public async Task<UserManagerBotDto> GetUserManagerBotAsync(string userId)
        {
            var _reposiory = _unitOfWork.GetRepository<AppUser>();

            return await _reposiory.Queryable().AsNoTracking()
                 .Where(x => x.Id == userId)
                 .Select(x => new UserManagerBotDto
                 {
                     //NumberOfThreads1080 = x.UserManagerBOTs.Where(i => i.ManagerBOT.LiveType == LiveType._1080).Sum(i => i.NumberOfThreads),
                     //NumberOfThreads4K = x.UserManagerBOTs.Where(i => i.ManagerBOT.LiveType == LiveType._4K).Sum(i => i.NumberOfThreads),
                     //Bot1080 = x.UserManagerBOTs.Where(i => i.LiveType == LiveType._1080)
                     //    .Select(i => i.ManagerBOTId).FirstOrDefault(),
                     //Bot4K = x.UserManagerBOTs.Where(i => i.LiveType == LiveType._4K)
                     //    .Select(i => i.ManagerBOTId).FirstOrDefault(),
                     UserName = x.UserName
                 }).FirstOrDefaultAsync();
        }

        public async Task<KeyValuePair<bool, string>> InsertBOTOfUserAsync(UserAddBOTAdminDto model)
        {
            try
            {
                //if (model.NumberOfThreads < 1)
                //{
                //    return new KeyValuePair<bool, string>(false, "Số luồng không hợp lệ!");
                //}
                //var _repositoryBOT = _unitOfWork.GetRepository<ManagerBOT>();
                //var botId = model.Bot1080.GetValueOrDefault() > 0 ? model.Bot1080 : model.Bot4k;
                //if (botId == null)
                //{
                //    return new KeyValuePair<bool, string>(false, "BOT Không tồn tại!");
                //}
                //var _repository = _unitOfWork.GetRepository<UserManagerBOT>();
                //var anyData = await _repository.ExistsAsync(x => x.UserId == model.UserId && x.ManagerBOTId == botId);
                //if (anyData)
                //{
                //    return new KeyValuePair<bool, string>(false, "Dữ liệu đã tồn tại!");
                //}
                //var botCurrent = await _repositoryBOT.GetFirstOrDefaultAsync(
                //    predicate: x => x.Id == botId);
                //if (botCurrent == null)
                //{
                //    return new KeyValuePair<bool, string>(false, "BOT Không tồn tại!");
                //}

                //_repository.Insert(new UserManagerBOT
                //{
                //    UserId = model.UserId,
                //    ManagerBOTId = botId.GetValueOrDefault(),
                //    LiveType = botCurrent.LiveType.GetValueOrDefault(),
                //    NumberOfThreads = model.NumberOfThreads,
                //    CreatedTime = DateTime.Now,
                //});
                //await _unitOfWork.SaveChangesAsync();
                return new KeyValuePair<bool, string>(true, string.Empty);

            }
            catch (Exception ex)
            {
                _logger.LogError($"Inser BOT User failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, $"Thêm BOT không thành công![{ex.Message}]");
            }
        }

        public async Task<KeyValuePair<bool, string>> ResetPassowrdAsync(ResetPasswordAdminDto model)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<AppUser>();

                var userCurrent = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.Id == model.UserId, disableTracking: false);
                if (userCurrent == null)
                {
                    return new KeyValuePair<bool, string>(false, "Người dùng không tồn tại!");
                }

                if (string.IsNullOrEmpty(model.Password))
                {
                    model.Password = RandomHelper.RandomString(6);
                }
                var hasher = new PasswordHasher<AppUser>();

                var passwordHash = hasher.HashPassword(null, model.Password);

                userCurrent.Password = model.Password;
                userCurrent.PasswordHash = passwordHash;
                userCurrent.UpdatedTime = DateTime.Now;
                userCurrent.UserUpdate = model.UserUpdate;

                _repository.Update(userCurrent);

                await _unitOfWork.SaveChangesAsync();

                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Resetpassword failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, "Reset password không thành công, vui lòng thử lại!");
            }
        }

        public async Task<KeyValuePair<bool, string>> UpdateAdminAsync(string userName)
        {
            var _repository = _unitOfWork.GetRepository<AppUser>();

            var roleManager = await _roleManager.FindByNameAsync("Admin");

            var userCurrent = await _repository.GetFirstOrDefaultAsync(
                predicate: x => x.UserName == userName,
                include: x => x.Include(i => i.UserRoles),
                disableTracking: false);

            if (userCurrent != null)
            {
                var isRoleCurrent = userCurrent.UserRoles.FirstOrDefault(x => x.RoleId == roleManager.Id);
                if (isRoleCurrent != null)
                {
                    userCurrent.UserRoles.Remove(isRoleCurrent);
                }
                else
                {
                    userCurrent.UserRoles.Add(new AppUserRole
                    {
                        RoleId = roleManager.Id,
                        UserId = userCurrent.Id,
                    });
                }

                _repository.Update(userCurrent);

                await _unitOfWork.SaveChangesAsync();
            }
            return new KeyValuePair<bool, string>(true, string.Empty);
        }

        public async Task<KeyValuePair<bool, string>> UpdateManagerAsync(string userName)
        {
            var _repository = _unitOfWork.GetRepository<AppUser>();

            var roleManager = await _roleManager.FindByNameAsync("Manager");

            var userCurrent = await _repository.GetFirstOrDefaultAsync(
                predicate: x => x.UserName == userName,
                include: x => x.Include(i => i.UserRoles),
                disableTracking: false);

            if (userCurrent != null)
            {
                var isRoleCurrent = userCurrent.UserRoles.FirstOrDefault(x => x.RoleId == roleManager.Id);
                if (isRoleCurrent != null)
                {
                    userCurrent.UserRoles.Remove(isRoleCurrent);
                }
                else
                {
                    userCurrent.UserRoles.Add(new AppUserRole
                    {
                        RoleId = roleManager.Id,
                        UserId = userCurrent.Id,
                    });
                }

                _repository.Update(userCurrent);

                await _unitOfWork.SaveChangesAsync();
            }
            return new KeyValuePair<bool, string>(true, string.Empty);
        }

        public async Task<KeyValuePair<bool, string>> UpdateTelegramUserAsync(UpdateTelegramDto model, string userId, bool isAdmin = false)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<AppUser>();
                var _repositoryRender = _unitOfWork.GetRepository<RenderHistory>();
                var _repositoryUserChannel = _unitOfWork.GetRepository<UserChannel>();
                var userCurrent = await _repository.GetFirstOrDefaultAsync(
                    predicate: x => x.Id == model.UserId, disableTracking: false);

                if (userCurrent == null)
                {
                    return new KeyValuePair<bool, string>(false, "Tài khoản không tồn tại!");
                }
                userCurrent.LinkTelegram = model.Telegram;
                if (isAdmin && !string.IsNullOrWhiteSpace(model.UserIdManager) && userCurrent.UserIdManager != model.UserIdManager)
                {
                    userCurrent.UserIdManager = model.UserIdManager;
                    var renders = await _repositoryRender.Queryable().AsNoTracking()
                        .Where(x => x.UserId == userCurrent.Id
                        && x.Status != SharedSignalrData.Enums.WorkStatus.Cancelled
                        && x.Status != SharedSignalrData.Enums.WorkStatus.Completed
                        ).Include(x => x.ChannelYoutube)
                        .ThenInclude(o => o.ManagerBOT).ToListAsync();
                    if (renders.Any())
                    {
                        foreach (var item in renders)
                        {
                            // item.Status = SharedSignalrData.Enums.WorkStatus.Cancelled;
                            await _botContextHub
                            .Clients
                            .Client(item.ChannelYoutube.ManagerBOT.ConnectionId)
                            .CancelWorkAsync(new Identy
                            {
                                ItemId = item.Id
                            });
                        }
                        //_repositoryRender.Update(it)
                    }
                    var channels =await _repositoryUserChannel.Queryable()
                        .Where(x => x.UserId == model.UserId)
                        .ToListAsync();
                    if (channels.Any())
                    {
                        _repositoryUserChannel.Delete(channels);
                    }

                }
                _repository.Update(userCurrent);
                await _unitOfWork.SaveChangesAsync();
                return new KeyValuePair<bool, string>(true, string.Empty);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Update Telegram failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, "Cập nhật không thành công!");
            }
        }






    }
}
