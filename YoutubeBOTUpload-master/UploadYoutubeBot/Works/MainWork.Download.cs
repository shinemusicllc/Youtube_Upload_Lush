using BaseSource.SharedSignalrData.Classes;
using BaseSource.SharedSignalrData.Interfaces;
using BaseSource.Shared.Enums;
using BaseSource.Shared.Helpers;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using TqkLibrary.Net.CloudStorage.GoogleDrive;
using UploadYoutubeBot.Helpers;
using UploadYoutubeBot.UI.ViewModels;
using Nito.AsyncEx;
using BaseSource.SharedSignalrData.Enums;

namespace UploadYoutubeBot.Works
{
    internal partial class MainWork
    {
        DateTime? _TimeStartDownload = null;
        async Task DownloadAsync()
        {
            if (WorkData.FileDatas.Any(x => string.IsNullOrWhiteSpace(x.Url) || string.IsNullOrWhiteSpace(x.Name)))
            {
                throw new Exception($"có file không có url hoặc tên");
            }

            using DownloadHelper downloadHelper = new DownloadHelper();
            foreach (var fileData in WorkData.FileDatas.Where(x => !x.Size.HasValue || x.Size == 0))
            {
                fileData.Size = await downloadHelper.GetFileSizeAsync(fileData, CancellationToken);
            }

            long totalSize = WorkData.FileDatas.Where(x => x.Size.HasValue).Sum(x => x.Size.Value);
            DateTime dateTime = DateTime.Now;
            long sizeDownloaded = 0;
            await UpdateDownloadAsync(sizeDownloaded, totalSize);


            _TimeStartDownload = DateTime.Now;
            foreach (var file in WorkData.FileDatas)
            {
                long fileSizeDownloaded = 0;
                await downloadHelper.DownloadAsync(file, WorkingDir, (x) =>
                {
                    sizeDownloaded += x;
                    fileSizeDownloaded += x;

                    if (dateTime < DateTime.Now)
                    {
                        dateTime = DateTime.Now.AddMilliseconds(500);

                        _ = UpdateDownloadAsync(sizeDownloaded, totalSize);
                    }
                }, CancellationToken);

                //if (fileSizeDownloaded != fileSize)
                //{
                //    throw new Exception($"Tải file '{file.Name}' thất bại, kích thước không khớp ({fileSize} != downloaded {fileSizeDownloaded})");
                //}

                //if (file.Size > 0)
                //{
                //    if (file.Size != fileSize)
                //    {
                //        throw new Exception($"Tải file '{file.Name}' thất bại, kích thước không khớp ({file.Size} != downloaded {fileSize})");
                //    }
                //}
                //else
                //{
                //    totalSize += fileSize;
                //}

                await UpdateDownloadAsync(sizeDownloaded, totalSize);
            }

            await UpdateDownloadAsync(sizeDownloaded, totalSize);

            //if (sizeDownloaded != totalSize)
            //{
            //    throw new Exception($"Tải file thất bại, kích thước không khớp");
            //}
        }
    }
}
