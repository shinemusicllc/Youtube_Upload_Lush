using BaseSource.SharedSignalrData.Classes;
using BaseSource.SharedSignalrData.Enums;
using BaseSource.SharedSignalrData.Interfaces;
using FFmpegArgs.Executes;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using TqkLibrary.Queues.TaskQueues;
using UploadYoutubeBot.UI.ViewModels;

namespace UploadYoutubeBot.Works
{
    internal partial class MainWork
    {
        protected IServerHub ServerHub { get; }
        Task UpdateErrorAsync(Exception exception)
        {
            WorkResponse workResponse = GetWorkResponse(WorkStatus.Error);
            workResponse.ExceptionInfo = new ExceptionInfo(exception);
            workResponse.Message = exception.Message;
            return WorkUpdateAsync(workResponse);
        }
        Task UpdateDownloadAsync(long sizeDownloaded, long totalSize)
        {
            WorkResponse workResponse = GetWorkResponse(WorkStatus.Downloading);
            if (totalSize > 0) workResponse.Percentage = sizeDownloaded * 1.0 / totalSize;
            return WorkUpdateAsync(workResponse);
        }
        Task UpdateRenderAsync(RenderProgress renderProgress, int renderStep, int totalStep, TimeSpan stepDuration)
        {
            WorkResponse workResponse = GetWorkResponse(WorkStatus.Rendering);
            workResponse.RenderResponse = new RenderResponse()
            {
                RenderStep = renderStep,
                TotalStep = totalStep,
                DurationRendered = renderProgress.Time,
                TotalDuration = stepDuration
            };
            workResponse.Percentage = renderProgress.Time.TotalMilliseconds / stepDuration.TotalMilliseconds;
            return WorkUpdateAsync(workResponse);
        }

        Task UpdateUploadAsync(double percent)
        {
            WorkResponse workResponse = GetWorkResponse(WorkStatus.Uploading);
            workResponse.Percentage = percent;
            return WorkUpdateAsync(workResponse);
        }

        Task WorkUpdateAsync(WorkResponse workResponse)
        {
            if (workResponse is null) throw new ArgumentNullException(nameof(workResponse));

            string log = string.Empty;
            switch (workResponse?.WorkStatus)
            {
                case WorkStatus.Downloading:
                case WorkStatus.Uploading:
                    log = $"{workResponse.WorkStatus} {workResponse.Percentage * 100}%";
                    break;

                case WorkStatus.Rendering:
                    log = $"{workResponse.WorkStatus} {workResponse.RenderResponse}";
                    break;

                case WorkStatus.Error:
                    log = $"{workResponse.WorkStatus} {workResponse.Message}\r\n" +
                        $"{workResponse.ExceptionInfo?.FullName}: {workResponse.ExceptionInfo?.Message}, {workResponse.ExceptionInfo?.StackTrace}";
                    break;

                default:
                    log = $"{workResponse.WorkStatus} {workResponse.Message}";
                    break;
            }
            WriteLog(log);
            return ServerHub.WorkUpdateAsync(workResponse);
        }

        WorkResponse GetWorkResponse(WorkStatus workStatus)
        {
            return new WorkResponse(WorkData.ItemId, WorkData.WorkId, workStatus)
            {
                TimeStartDownload = _TimeStartDownload,
                TimeStartRender = _TimeStartRender,
                TimeStartUpload = _TimeStartUpload,
                TimeCompleted = _TimeCompleted,
                VideoUploadedUrl = _uploadedUrl,
            };
        }
    }
}
