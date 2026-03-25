using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UploadYoutubeBot.Attributes;

namespace UploadYoutubeBot.Enums
{
    internal enum YoutubeChannelMenu
    {
        [Name("Thêm Profile")]AddProfile,
        [Name("Xóa Profiles đã chọn")] DeleteSelectedProfile,
        [Name("Mở không selenium")] OpenNonSelenium,
        [Name("Lấy thông tin kênh")] CheckYoutubeProfile,
        [Name("Thêm Profile có sẵn từ thư mục profile")] AddProfileExist
    }
}
