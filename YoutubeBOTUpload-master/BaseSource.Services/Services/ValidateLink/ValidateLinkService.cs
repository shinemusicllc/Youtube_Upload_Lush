using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using TqkLibrary.Net.CloudStorage.Dropbox;
using TqkLibrary.Net.CloudStorage.GoogleDrive;
using TqkLibrary.Net.CloudStorage.OneDrive;
using BaseSource.Shared.Helpers;
using BaseSource.Shared.Enums;
using BaseSource.SharedSignalrData.Enums;

namespace BaseSouce.Services.Services.ValidateLink
{
    public class ValidateLinkService : IValidateLinkService, IDisposable
    {
        readonly HttpClientHandler _httpClientHandler;
        readonly GoogleDriveApiNonLogin _googleDriveApiNonLogin;
        readonly OneDriveApiNonLogin _oneDriveApiNonLogin;
        readonly DropboxApiNonLogin _dropboxApiNonLogin;

        public ValidateLinkService()
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
        ~ValidateLinkService()
        {
            Dispose(false);
        }
        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }
        void Dispose(bool isDisposing)
        {
            _googleDriveApiNonLogin.Dispose();
            _dropboxApiNonLogin.Dispose();
            _oneDriveApiNonLogin.Dispose();
            _httpClientHandler.Dispose();
        }

        public UrlType? GetUrlType(string url)
        {
            Uri.TryCreate(url, UriKind.RelativeOrAbsolute, out Uri? result);
            return GetUrlType(result);
        }

        public UrlType? GetUrlType(Uri? uri)
        {
            switch (uri?.Host)
            {
                case "1drv.ms":
                    return UrlType.OneDrive;

                case "www.dropbox.com":
                    return UrlType.Dropbox;

                case "drive.google.com":
                    return UrlType.GoogleDrive;

                default:
                    return null;
            }
        }


        public async Task<KeyValuePair<bool, string>> ValidateLinkAsync(string link, string? name = null)
        {
            if (string.IsNullOrWhiteSpace(link))
                return new KeyValuePair<bool, string>(false, $"Link {name} rỗng");

            if (!Uri.TryCreate(link, UriKind.RelativeOrAbsolute, out Uri? uri))
                return new KeyValuePair<bool, string>(false, $"Link {name} sai định dạng");

            try
            {
                switch (GetUrlType(uri))
                {
                    case UrlType.OneDrive://oneDrive
                        var data = await _oneDriveApiNonLogin.DecodeShortLinkAsync(uri);
                        await _oneDriveApiNonLogin.GetMetadataAsync(data);
                        return new KeyValuePair<bool, string>(true, string.Empty);

                    case UrlType.Dropbox://dropbox
                        await _dropboxApiNonLogin.GetCookieAsync(uri);
                        using (System.IO.Stream stream = await _dropboxApiNonLogin.DownloadFileAsync(uri.ToString()))
                        {

                        }
                        return new KeyValuePair<bool, string>(true, string.Empty);

                    case UrlType.GoogleDrive://google drive
                        var driveVideoItem = GoogleDriveHelper.TryParse(link);
                        if (driveVideoItem is null ||
                            driveVideoItem.LinkType != GoogleDriveLinkType.File)
                            return new KeyValuePair<bool, string>(false, $"Link {name} không hỗ trợ hoặc không hợp lệ");

                        await _googleDriveApiNonLogin.GetMetadataAsync(driveVideoItem.ID);
                        return new KeyValuePair<bool, string>(true, string.Empty);

                    default:
                        return new KeyValuePair<bool, string>(false, $"Không {name} hỗ trợ '{uri.Host}'");
                }
            }
            catch (Exception ex)
            {
                return new KeyValuePair<bool, string>(false, $"Lỗi {ex}");
            }
        }
    }
}
