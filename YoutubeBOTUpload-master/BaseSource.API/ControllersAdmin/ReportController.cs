using BaseSource.ViewModels.Common;
using BaseSource.Services.Services.Report;
using Microsoft.AspNetCore.Mvc;

namespace BaseSource.API.ControllersAdmin
{
    public class ReportController : BaseAdminApiController
    {
        private readonly IReportService _reportService;
        public ReportController(IReportService reportService)
        {
            _reportService = reportService;
        }
        [HttpGet]
        [Route("/api/admin/report")]
        public async Task<IActionResult> GetReportData([FromQuery] string managers)
        {
            var result = await _reportService.GetReportChannelAsync(UserId,managers, IsAdmin);
            return Ok(new ApiSuccessResult<object>(result));
        }
    }
}
