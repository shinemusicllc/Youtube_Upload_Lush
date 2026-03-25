using BaseSource.SharedSignalrData.Classes;
using BaseSource.ViewModels.Render;
using BaseSource.ViewModels.Report;
using EFCore.UnitOfWork.PageList;

namespace BaseSource.Services.Services.Render
{
    public interface IRenderClientService
    {
        Task<KeyValuePair<bool,string>> CreateAsync(string userId, RenderCreateDto model);
        Task<KeyValuePair<bool, string>> UpdateAsync(string userId, int id, RenderUpdateDto model);
        Task<KeyValuePair<bool, string>> StartAsync(string userId, int id);
        Task<KeyValuePair<bool, string>> StopAsync(string userId, int id);
        Task<KeyValuePair<bool, string>> DeleteAsync(string userId, int id);
        Task<IPagedList<RenderHistoryDto>> GetByFilterAsync(string userId, RenderRequestDto model);
        Task<KeyValuePair<bool, string>> CloneAsync(string userId, int id);
        Task<KeyValuePair<bool, string>> ValidateLinkAsync(string link);
        Task<RenderHistoryDto> GetRenderByIdAsync(string userId, int id);
        Task<KeyValuePair<bool, string>> DeleteWeeklyAsync();
        Task<KeyValuePair<bool, string>> ScheduleRenderAsync();
        Task<RenderReportClientDto> GetReportRenderAsync(string userId);
    }
}
