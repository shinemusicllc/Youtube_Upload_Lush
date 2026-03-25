using BaseSource.Shared.Enums;

namespace BaseSource.Shared.Interfaces
{
    public interface IGoogleDriveItemResult
    {
        string ID { get; }
        string? ResourceKey { get; }
        GoogleDriveLinkType LinkType { get; }
    }
}
