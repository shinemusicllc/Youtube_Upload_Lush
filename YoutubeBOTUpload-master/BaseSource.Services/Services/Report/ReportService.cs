using AutoMapper;
using BaseSource.Data.EF;
using BaseSource.Data.Entities;
using BaseSource.SharedSignalrData.Enums;
using BaseSource.ViewModels.Report;
using EFCore.UnitOfWork;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace BaseSource.Services.Services.Report
{
    public class ReportService : IReportService
    {
        private readonly IUnitOfWork _unitOfWork;
        private readonly ILogger<ReportService> _logger;
        private readonly IMapper _mapper;
        public ReportService(
            IUnitOfWork<BaseSourceDbContext> unitOfWork,
            ILogger<ReportService> logger,
            IMapper mapper
            )
        {
            _unitOfWork = unitOfWork;
            _logger = logger;
            _mapper = mapper;
        }
        public async Task<ReportDto> GetReportChannelAsync(string userId, string managers, bool isAdmin = false)
        {
            var _repositoryUser = _unitOfWork.GetRepository<AppUser>();
            var _repositoryChannel = _unitOfWork.GetRepository<ChannelYoutube>();
            var _repositoryBOT = _unitOfWork.GetRepository<ManagerBOT>();
            var _repositoryRender = _unitOfWork.GetRepository<RenderHistory>();

            
            var data = new ReportDto();
            if (isAdmin)
            {
                if (!string.IsNullOrWhiteSpace(managers))
                {
                    var lstManagers = new List<string>();
                    lstManagers = managers.Split(',').ToList();
                    if (lstManagers.Any())
                    {
                        data.TotalBot = await _repositoryBOT.Queryable()
                            .Where(x => x.DeletedTime == null && lstManagers.Any(i => i == x.UserIdManager)).CountAsync();
                        data.TotalBotConnected = await _repositoryBOT.Queryable()
                            .Where(x => x.DeletedTime == null
                            && x.Status == Shared.Enums.ManagerBOTStatus.Connected
                            && lstManagers.Any(i => i == x.UserIdManager)
                            ).CountAsync();
                        data.TotalChannel = await _repositoryChannel
                            .Queryable()
                            .Where(x => x.DeletedTime == null
                            && lstManagers.Any(i => i == x.ManagerBOT.UserIdManager)).CountAsync();

                        data.TotalUser = await _repositoryUser.Queryable().AsNoTracking()
                            .Where(x => !x.UserRoles.Any() && x.DeletedTime == null
                            && lstManagers.Any(i => i == x.UserIdManager))
                            .CountAsync();
                        data.TotalManager = lstManagers.Count();

                        data.TotalRender = await _repositoryRender.Queryable()
                            .AsNoTracking()
                            .Where(x => lstManagers.Any(i => i == x.AppUser.UserIdManager)).CountAsync();
                        data.TotalRenderInRun = await _repositoryRender.Queryable().AsNoTracking()
                            .Where(x => lstManagers.Any(i => i == x.AppUser.UserIdManager)
                            && (x.Status == WorkStatus.Rendering || x.Status == WorkStatus.Downloading))
                            .CountAsync();
                        data.TotalRenderUpload = await _repositoryRender.Queryable().AsNoTracking()
                            .Where(x => x.Status == WorkStatus.Uploading && lstManagers.Any(i => i == x.AppUser.UserIdManager)).CountAsync();
                        data.TotalRenderPending = await _repositoryRender.Queryable().AsNoTracking()
                            .Where(x => lstManagers.Any(i => i == x.AppUser.UserIdManager) && (
                            x.Status == WorkStatus.Pending
                            || x.Status == WorkStatus.Queueing
                            || x.Status == WorkStatus.Schedule)).CountAsync();
                        return data;
                    }



                }

                data.TotalBot = await _repositoryBOT.Queryable().Where(x => x.DeletedTime == null).CountAsync();
                data.TotalBotConnected = await _repositoryBOT.Queryable()
                    .Where(x => x.DeletedTime == null
                    && x.Status == Shared.Enums.ManagerBOTStatus.Connected).CountAsync();
                data.TotalChannel = await _repositoryChannel.Queryable().Where(x => x.DeletedTime == null).CountAsync();
                data.TotalUser = await _repositoryUser.Queryable().AsNoTracking()
                    .Where(x => !x.UserRoles.Any() && x.DeletedTime == null).CountAsync();
                data.TotalManager = await _repositoryUser.Queryable().AsNoTracking()
                    .Where(x => x.DeletedTime == null && x.UserRoles.Any(x => x.RoleId == "c1105ce5-9dbc-49a9-a7d5-c963b6daa62a"))
                    .CountAsync();

                data.TotalRender = await _repositoryRender.Queryable().AsNoTracking().CountAsync();
                data.TotalRenderInRun = await _repositoryRender.Queryable().AsNoTracking()
                    .Where(x => x.Status == WorkStatus.Rendering || x.Status == WorkStatus.Downloading).CountAsync();
                data.TotalRenderUpload = await _repositoryRender.Queryable().AsNoTracking()
                    .Where(x => x.Status == WorkStatus.Uploading).CountAsync();
                data.TotalRenderPending = await _repositoryRender.Queryable().AsNoTracking()
                    .Where(x => x.Status == WorkStatus.Pending
                    || x.Status == WorkStatus.Queueing
                    || x.Status == WorkStatus.Schedule).CountAsync();
                return data;
            }
            else
            {
                data.TotalBot = await _repositoryBOT.Queryable()
                    .Where(x => x.DeletedTime == null && x.UserIdManager == userId).CountAsync();

                data.TotalBotConnected = await _repositoryBOT.Queryable()
                .Where(x => x.DeletedTime == null
                && x.UserIdManager == userId
                && x.Status == Shared.Enums.ManagerBOTStatus.Connected).CountAsync();

                data.TotalChannel = await _repositoryChannel.Queryable().Where(x => x.DeletedTime == null
                && (x.ManagerBOT.UserIdManager == userId)).CountAsync();
                data.TotalUser = await _repositoryUser.Queryable().AsNoTracking()
                    .Where(x => !x.UserRoles.Any() && x.DeletedTime == null && (x.UserIdManager == userId)).CountAsync();
                //data.TotalManager = await _repositoryUser.Queryable().AsNoTracking()
                //    .Where(x => x.DeletedTime == null && x.Id == userId)
                //    .CountAsync();
                data.TotalManager = 1;

                data.TotalRender = await _repositoryRender.Queryable().AsNoTracking()
                    .Where(x => x.DeletedTime == null && (x.AppUser.UserIdManager == userId || x.UserId == userId)).CountAsync();
                data.TotalRenderInRun = await _repositoryRender.Queryable().AsNoTracking()
                    .Where(x => x.Status == WorkStatus.Rendering || x.Status == WorkStatus.Downloading
                    && (x.AppUser.UserIdManager == userId || x.UserId == userId)).CountAsync();
                data.TotalRenderUpload = await _repositoryRender.Queryable().AsNoTracking()
                    .Where(x => x.Status == WorkStatus.Uploading
                    && (x.UserId == userId || x.AppUser.UserIdManager == userId)).CountAsync();
                data.TotalRenderPending = await _repositoryRender.Queryable().AsNoTracking()
                    .Where(x => x.DeletedTime == null
                    && (x.Status == WorkStatus.Pending
                    || x.Status == WorkStatus.Queueing
                    || x.Status == WorkStatus.Schedule)
                    && (x.UserId == userId || x.AppUser.UserIdManager == userId)).CountAsync();
                return data;
            }
        }
    }
}
