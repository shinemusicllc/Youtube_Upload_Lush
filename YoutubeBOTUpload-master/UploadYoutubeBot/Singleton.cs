using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using TqkLibrary.WpfUi;
using UploadYoutubeBot.DataClass;

namespace UploadYoutubeBot
{
    internal static class Singleton
    {
        static Singleton()
        {
            Directory.CreateDirectory(LogDir);
            Directory.CreateDirectory(BaseWorkingDir);
            Setting = new SaveSettingData<SettingData>(SettingJson);
            FFMpegCore.GlobalFFOptions.Configure(x => x.BinaryFolder = FFmpegDir);
        }
        internal static string ExeDir { get; } = Directory.GetCurrentDirectory();
        internal static DirectoryInfo ExeDirInfo { get; } = new DirectoryInfo(ExeDir);
        internal static string LogDir { get; } = Path.Combine(ExeDir, "Logs");
        internal static string AppDataDir { get; } = Path.Combine(ExeDir, "AppData");
        internal static string FFmpegDir { get; } = Path.Combine(AppDataDir, "FFmpeg");
        internal static string FFmpeg { get; } = Path.Combine(FFmpegDir, "ffmpeg.exe");
        internal static string ProfilesDir { get; } = Path.Combine(ExeDir, "Profiles");
        internal static string ChromeDriverDir { get; } = Path.Combine(ExeDir, "ChromeDriver");
        internal static string SettingJson { get; } = Path.Combine(ExeDir, "Setting.json");
        internal static string ListYoutubeChannelPath { get; } = Path.Combine(ExeDir, "YoutubeChannels.json");
        public static string BaseWorkingDir { get; } = Path.Combine(ExeDir, "BaseWorkingDir");

        internal static SaveSettingData<SettingData> Setting { get; }
    }
}
