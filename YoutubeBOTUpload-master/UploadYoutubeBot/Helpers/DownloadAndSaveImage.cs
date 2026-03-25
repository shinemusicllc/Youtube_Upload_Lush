using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace UploadYoutubeBot.Helpers
{
    internal static class DownloadAndSaveImage
    {
        static readonly HttpClient httpClient = new HttpClient();


        public static async Task DownloadAsync(string url, string savePath, CancellationToken cancellationToken = default)
        {
            using HttpRequestMessage httpRequestMessage = new HttpRequestMessage(HttpMethod.Get, url);
            using HttpResponseMessage httpResponseMessage = await httpClient.SendAsync(httpRequestMessage, HttpCompletionOption.ResponseHeadersRead, cancellationToken);
            httpResponseMessage.EnsureSuccessStatusCode();
            using Stream stream = await httpResponseMessage.Content.ReadAsStreamAsync();
            using FileStream fileStream = new FileStream(savePath, FileMode.OpenOrCreate, FileAccess.Write, FileShare.Read);
            await stream.CopyToAsync(fileStream, 81920, cancellationToken);
        }
    }
}
