using BaseSource.SharedSignalrData.Classes;
using BaseSource.ViewModels.Render;
using BaseSource.ViewModels.RenderAdmin;
using EFCore.UnitOfWork.PageList;

namespace BaseSource.Services.Services.RenderAdmin
{
    public interface IRenderAdminService
    {
        Task<IPagedList<RenderAdminInfoDto>> GetAllAsync(RenderAdminRequestDto model, string userId, bool isAdmin = false);
        Task<List<RenderAdminInfoDto>> GetAllByChannelAsync(int channelId);
        Task<RenderHistoryDto> GetByIdAsync(int id);
        Task<KeyValuePair<bool, string>> WorkUpdateAsync(WorkResponse model);
        Task<KeyValuePair<bool, string>> DeleteAsync(string username);
    }
}
