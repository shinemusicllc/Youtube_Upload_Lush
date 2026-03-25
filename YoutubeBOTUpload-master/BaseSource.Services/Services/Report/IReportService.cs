using BaseSource.ViewModels.Report;

namespace BaseSource.Services.Services.Report
{
    public interface IReportService
    {
        Task<ReportDto> GetReportChannelAsync(string userId,string managers, bool isAdmin = false);
    }
}
