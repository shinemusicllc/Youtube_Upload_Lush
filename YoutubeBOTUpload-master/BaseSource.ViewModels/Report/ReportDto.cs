namespace BaseSource.ViewModels.Report
{
    public class ReportDto
    {
        public int TotalBot { get; set; }
        public int TotalBotConnected { get; set; }
        public int TotalUser { get; set; }
        public int TotalManager { get; set; }
        public int TotalChannel { get; set; }
        public int TotalRender { get; set; }
        public int TotalRenderInRun { get; set; }
        public int TotalRenderUpload { get; set; }
        public int TotalRenderPending { get; set;}
    }
    public class RenderReportClientDto
    {
        public int TotalRender { get; set; }
        public int TotalRenderInRun { get; set; }
        public int TotalRenderUpload { get; set; }
        public int TotalRenderPending { get; set; }
    }
}
