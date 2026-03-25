using BaseSource.SharedSignalrData.Classes;
using BaseSource.SharedSignalrData.Enums;
using BaseSource.SharedSignalrData.Interfaces;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using TqkLibrary.Queues.TaskQueues;
using UploadYoutubeBot.DataClass;
using UploadYoutubeBot.UI.ViewModels;

namespace UploadYoutubeBot.Works
{
    internal partial class MainWork
    {
        DateTime? _TimeStartUpload = null;
        string _uploadedUrl = null;
        async Task UploadAsync(string filePath)
        {
            try
            {
                UpdatePercent(0);
                _TimeStartUpload = DateTime.Now;
                YoutubeChannel.ChromeProfileVM.YoutubeProfile.LogCallback += WriteLog;
                await YoutubeChannel.ChromeProfileVM.YoutubeProfile.OpenChromeAsync();
                _uploadedUrl = await YoutubeChannel.ChromeProfileVM.YoutubeProfile.YoutubeUploadAsync(new VideoUploadInfo()
                    {
                        VideoPath = filePath,
                        IsDraft = true,
                        IsMakeForKid = false,
                        Title = WorkData.UploadTitleName,
                    },
                    UpdatePercent,
                    null,
                    CancellationToken);
                if (string.IsNullOrWhiteSpace(_uploadedUrl))
                {
                    WorkResponse workResponse = GetWorkResponse(WorkStatus.Error);
                    workResponse.Message = "Lấy url thất bại";
                    await WorkUpdateAsync(workResponse);
                }
                else
                {
                    UpdatePercent(100);
                }
            }
            finally
            {
                YoutubeChannel.ChromeProfileVM.YoutubeProfile.LogCallback -= WriteLog;
            }
        }

        async void UpdatePercent(int percent)
        {
            await UpdateUploadAsync(percent * 0.01);
        }
    }
}
