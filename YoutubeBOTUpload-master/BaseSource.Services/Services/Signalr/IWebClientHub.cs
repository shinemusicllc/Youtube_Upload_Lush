using BaseSource.ViewModels.Render;

namespace BaseSource.Services.Services.Signalr
{
    public interface IWebClientHub
    {
        Task RenderInfo(RenderHistoryDto model);
    }
}
