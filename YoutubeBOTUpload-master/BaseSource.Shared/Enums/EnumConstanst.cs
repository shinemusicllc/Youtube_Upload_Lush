using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.Shared.Enums
{
    public enum ServicePackType : byte
    {
        _1080 = 1,
        _4K = 2,
    }
    public enum LiveType : byte
    {
        _1080 = 1,
        _4K = 2,
    }
    public enum PlatformType : byte
    {
        Youtube = 1,
        Facebook = 2
    }
    public enum LiveOrder : byte
    {
        Sequence = 1,
        Random = 2
    }

    public enum ManagerBOTStatus : byte
    {
        Connected = 1,
        Disconnected = 2,
    }
    public enum OrderStatus : byte
    {
        Success = 1,
        Waiting = 2,
        Cancel = 3
    }
    public enum StreamStatus : byte
    {
        Encode = 1,
        Cancel = 2,
    }
    public enum SteamLogStatus : byte
    {
        Download = 1,
        Render = 2,
        Running = 3
    }

    public enum RenderStatus : int
    {
        Render = 0,
        Cancel = 1,
        Unknown = 2
    }
#if NET6_0_OR_GREATER
    public enum RenderAction
    {
        [Display(Name = "Không xác định")]
        [Description("Không xác định")]
        Unknown = 0,
        [Display(Name = "Chờ Encode")]
        [Description("Chờ Encode")]
        Waiting = 1,
        [Display(Name = "Loading")]
        [Description("Loading")]
        Loading = 2,
        [Display(Name = "Đang dowload")]
        [Description("Đang dowload")]
        Downloading = 3,
        [Display(Name = "Đang Encode")]
        [Description("Đang Encode")]
        Encoding = 4,
        [Display(Name = "Đang Upload Video")]
        [Description("Đang Upload Video")]
        Uploading = 5,
        [Display(Name = "Hoàn thành")]
        [Description("Hoàn thành")]
        Done = 6,
        [Display(Name = "Hủy")]
        [Description("Hủy")]
        Cancel = 7,
        [Display(Name = "Không tìm thấy")]
        [Description("Không tìm thấy")]
        NotFound = (1 << 30) | Error,
        Error = 1 << 31// error only -> Error ^ Error = Unknown
    }
#endif
}
