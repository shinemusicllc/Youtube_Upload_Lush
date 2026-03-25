using BaseSource.SharedSignalrData.Classes;
using BaseSource.SharedSignalrData.Enums;
using System;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using TqkLibrary.Net.CloudStorage.GoogleDrive;
using TqkLibrary.Net.CloudStorage.Dropbox;
using TqkLibrary.Net.CloudStorage.OneDrive;

namespace UploadYoutubeBot.Helpers
{
    internal class DownloadHelper : IDisposable
    {
        //https://drive.google.com/file/d/1I0zTP9I5XIcDitHa_4hKug5FM8pCV-EY/view?usp=share_link
        readonly Regex regex_driveFile = new Regex("(?<=\\/d\\/)[a-zA-Z0-9_-]+(?=\\/|$)");

        readonly HttpClientHandler _httpClientHandler;
        readonly HttpClient _httpClient;
        readonly GoogleDriveApiNonLogin _googleDriveApiNonLogin;
        readonly OneDriveApiNonLogin _oneDriveApiNonLogin;
        readonly DropboxApiNonLogin _dropboxApiNonLogin;
        public DownloadHelper()
        {
            _httpClientHandler = new HttpClientHandler()
            {
                AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate,
                AllowAutoRedirect = true,
            };
            _googleDriveApiNonLogin = new GoogleDriveApiNonLogin(_httpClientHandler, false);
            _dropboxApiNonLogin = new DropboxApiNonLogin(_httpClientHandler, false);
            _oneDriveApiNonLogin = new OneDriveApiNonLogin();
        }

        public void Dispose()
        {
            _googleDriveApiNonLogin.Dispose();
            _dropboxApiNonLogin.Dispose();
            _oneDriveApiNonLogin.Dispose();
            _httpClientHandler.Dispose();
        }


        public async Task<long?> GetFileSizeAsync(FileData fileData, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(fileData?.Url)) throw new ArgumentNullException($"{nameof(FileData)}.{nameof(FileData.Url)}");
            switch (fileData.UrlType)
            {
                case UrlType.GoogleDrive:
                    {
                        string fileId = string.Empty;

                        Match match = regex_driveFile.Match(fileData.Url);
                        if (match.Success)
                            fileId = match.Value;


                        if (string.IsNullOrWhiteSpace(fileId))
                        {
                            throw new NotSupportedException($"Not support link type: {fileData.Url}");
                        }
                        else
                        {
                            var data = await _googleDriveApiNonLogin.GetMetadataAsync(fileId, cancellationToken);
                            return data.FileSize;
                        }
                    }
                case UrlType.OneDrive:
                    {
                        var data = await _oneDriveApiNonLogin.DecodeShortLinkAsync(new Uri(fileData.Url), cancellationToken);
                        var metaData = await _oneDriveApiNonLogin.GetMetadataAsync(data, cancellationToken);
                        return metaData.Size;
                    }

                default:
                    return null;
            }
        }


        public async Task DownloadAsync(FileData fileData, string workingDir, Action<int> dataTransfer, CancellationToken cancellationToken = default)
        {
            if (string.IsNullOrWhiteSpace(fileData?.Url)) throw new ArgumentNullException($"{nameof(FileData)}.{nameof(FileData.Url)}");
            if (string.IsNullOrWhiteSpace(workingDir)) throw new ArgumentNullException($"{nameof(workingDir)}");
            Directory.CreateDirectory(workingDir);
            string savePath = Path.Combine(workingDir, fileData.Name);
            switch (fileData.UrlType)
            {
                case UrlType.Normal:
                    {
                        await DownloadRaw(fileData.Url, savePath, dataTransfer, cancellationToken);
                        break;
                    }

                case UrlType.GoogleDrive:
                    {
                        string fileId = string.Empty;

                        Match match = regex_driveFile.Match(fileData.Url);
                        if (match.Success)
                            fileId = match.Value;


                        if (string.IsNullOrWhiteSpace(fileId))
                        {
                            throw new NotSupportedException($"Not support link type: {fileData.Url}");
                        }
                        else
                        {
                            using Stream stream = await _googleDriveApiNonLogin.DownloadFileAsync(fileId, cancellationToken);
                            using TrackStream trackStream = new TrackStream(stream, dataTransfer);
                            using FileStream fileStream = new FileStream(savePath, FileMode.CreateNew, FileAccess.Write, FileShare.Read);
                            await trackStream.CopyToAsync(fileStream, 81920, cancellationToken).ConfigureAwait(false);
                        }
                        break;
                    }

                case UrlType.Dropbox:
                    {
                        using Stream stream = await _dropboxApiNonLogin.DownloadFileAsync(fileData.Url, cancellationToken);
                        using TrackStream trackStream = new TrackStream(stream, dataTransfer);
                        using FileStream fileStream = new FileStream(savePath, FileMode.CreateNew, FileAccess.Write, FileShare.Read);
                        await trackStream.CopyToAsync(fileStream, 81920, cancellationToken).ConfigureAwait(false);
                        break;
                    }
                case UrlType.OneDrive:
                    {
                        var data = await _oneDriveApiNonLogin.DecodeShortLinkAsync(new Uri(fileData.Url), cancellationToken);
                        using Stream stream = await _oneDriveApiNonLogin.DownloadFileAsync(data, cancellationToken);
                        using TrackStream trackStream = new TrackStream(stream, dataTransfer);
                        using FileStream fileStream = new FileStream(savePath, FileMode.CreateNew, FileAccess.Write, FileShare.Read);
                        await trackStream.CopyToAsync(fileStream, 81920, cancellationToken).ConfigureAwait(false);
                        break;
                    }

                default:
                    throw new NotSupportedException($"{fileData.UrlType}");
            }

        }

        async Task DownloadRaw(string url, string filePath, Action<int> dataTransfer, CancellationToken cancellationToken = default)
        {
            using HttpRequestMessage httpRequestMessage = new HttpRequestMessage(HttpMethod.Get, url);
            using HttpResponseMessage httpResponseMessage = await _httpClient.SendAsync(httpRequestMessage, cancellationToken);
            using Stream stream = await httpResponseMessage.EnsureSuccessStatusCode().Content.ReadAsStreamAsync();
            using TrackStream trackStream = new TrackStream(stream, dataTransfer);
            using FileStream fileStream = new FileStream(filePath, FileMode.CreateNew, FileAccess.Write, FileShare.Read);
            await trackStream.CopyToAsync(fileStream, 81920, cancellationToken);
        }
    }
}
