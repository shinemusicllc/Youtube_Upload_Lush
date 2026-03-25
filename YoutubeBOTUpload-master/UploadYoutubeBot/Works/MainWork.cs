using BaseSource.SharedSignalrData.Classes;
using BaseSource.SharedSignalrData.Enums;
using BaseSource.SharedSignalrData.Interfaces;
using FFmpegArgs.Executes;
using FFmpegArgs.Executes.Exceptions;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using TqkLibrary.Queues.TaskQueues;
using UploadYoutubeBot.Exceptions;
using UploadYoutubeBot.UI.ViewModels;

namespace UploadYoutubeBot.Works
{
    internal partial class MainWork : BaseWork, IWork
    {
        public WorkData WorkData { get; }
        protected string WorkingDir { get; }
        public MainWork(
            YoutubeChannelVM youtubeChannelVM,
            WorkData workData,
            IServerHub serverHub
            )
            : base(
                 youtubeChannelVM
                 )
        {
            this.WorkData = workData ?? throw new ArgumentNullException(nameof(workData));
            this.ServerHub = serverHub ?? throw new ArgumentNullException(nameof(serverHub));

            WorkingDir = Path.Combine(Singleton.BaseWorkingDir, $"{WorkData.ItemId}_{WorkData.WorkId}");
        }

        DateTime? _TimeCompleted = null;
        public override async Task DoWork()
        {
            try
            {
                MainWVM.WriteLog($"[{WorkData.ItemId}-{WorkData.WorkId}] Starting");
                foreach (var chr in Path.GetInvalidFileNameChars())
                {
                    if (WorkData.UploadTitleName.Contains(chr))
                    {
                        throw new Exception($"Tên chứa ký tự không hợp lệ ( {chr} ) : {WorkData.UploadTitleName}");
                    }
                }

                //force rename
                int videoLoopIndex = 0;
                int audioLoopIndex = 0;
                foreach (var item in WorkData.FileDatas)
                {
                    string extension = item.FileType switch
                    {
                        FileType.Video => ".mp4",
                        FileType.Audio => ".mp3",
                        _ => throw new NotSupportedException(item.FileType.ToString()),
                    };

                    switch (item.FilePosition)
                    {
                        case FilePosition.Intro:
                        case FilePosition.Outro:
                            item.Name = $"{item.FilePosition}{extension}";
                            break;

                        case FilePosition.Loop:
                            int index = item.FileType switch
                            {
                                FileType.Video => videoLoopIndex++,
                                FileType.Audio => audioLoopIndex++,
                                _ => throw new NotSupportedException(item.FileType.ToString()),
                            };

                            item.Name = $"{item.FilePosition}{index}{extension}";
                            break;
                    }
                }


                await DownloadAsync();
                string filePath = await RenderAsync();
                await UploadAsync(filePath);
                _TimeCompleted = DateTime.Now;
                WorkResponse workResponse = GetWorkResponse(WorkStatus.Completed);
                await WorkUpdateAsync(workResponse);
            }
            catch (OperationCanceledException)
            {
                WorkResponse workResponse = GetWorkResponse(WorkStatus.Cancelled);
                await WorkUpdateAsync(workResponse);
            }
            catch (FFmpegRenderException fre)
            {
                WorkResponse workResponse = GetWorkResponse(WorkStatus.Error);
                workResponse.ExceptionInfo = new ExceptionInfo(fre);
                if (fre.OutputDatas.Any(x => x.Contains("No space left on device")))
                {
                    workResponse.Message = "Hết ổ cứng";
                }
                else
                {
                    workResponse.Message = $"FFmpeg ExitCode: {fre.ExitCode}\r\n{string.Join("\r\n", fre.OutputDatas)}";
                }
                await WorkUpdateAsync(workResponse);
            }
            catch (YtcpAuthConfirmationDialogException ex)
            {
                WorkResponse workResponse = GetWorkResponse(WorkStatus.Error);
                workResponse.ExceptionInfo = new ExceptionInfo(ex);
                workResponse.Message = $"Cần đăng nhập lại";
                await WorkUpdateAsync(workResponse);
                try
                {
                    await YoutubeChannel.ChromeProfileVM.YoutubeProfile.HoldOnChromeOpenAsync(CancellationToken);
                }
                catch
                {

                }
            }
            catch (Exception ex)
            {
                if (ex is AggregateException ae) ex = ae.InnerException;
                await UpdateErrorAsync(ex);
            }
            finally
            {
                YoutubeChannel.ChromeProfileVM.YoutubeProfile.CloseChrome();
                await Task.Delay(1000);
                WriteLog($"Xóa thư mục render");
                Directory.Delete(WorkingDir, true);
                WriteLog($"Xóa thư mục {YoutubeChannel.ChromeProfileVM.ProfileName}\\Default\\IndexedDB");
                await YoutubeChannel.ChromeProfileVM.YoutubeProfile.DeleteIndexedDB();
                WriteLog($"Xóa hoàn tất");
            }
        }


        void WriteLog(string log)
        {
            MainWVM.WriteLog($"[{WorkData.ItemId}-{WorkData.WorkId}] {log}", "MainWork Log");
        }

        public override bool Equals(object obj)
        {
            if (ReferenceEquals(this, obj))
            {
                return true;
            }
            if (obj is MainWork mainWork && mainWork.WorkData.ItemId == this.WorkData.ItemId)
            {
                return true;
            }
            return false;
        }
        public override int GetHashCode()
        {
            return this.WorkData.ItemId.GetHashCode();
        }
    }
}
