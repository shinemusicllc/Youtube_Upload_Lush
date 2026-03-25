using BaseSource.SharedSignalrData.Enums;

namespace BaseSouce.Services.Services.ValidateLink
{
    public interface IValidateLinkService
    {
        UrlType? GetUrlType(string url);
        UrlType? GetUrlType(Uri? uri);
        Task<KeyValuePair<bool, string>> ValidateLinkAsync(string link, string? name = null);
    }
}
