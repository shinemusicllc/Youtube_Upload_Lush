using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using TqkLibrary.WpfUi;
using UploadYoutubeBot.DataClass;

namespace UploadYoutubeBot.UI.ViewModels
{
    internal class ListViewYoutubeChannelSettingUIProxy : BaseViewModel
    {
        static SaveSettingData<ListViewYoutubeChannelSettingUI> YoutubeChannelSettingUI { get; }
            = new SaveSettingData<ListViewYoutubeChannelSettingUI>(Path.Combine(Singleton.ExeDir, "ListViewYoutubeChannelSettingUI.json"));
        static void Save() => YoutubeChannelSettingUI.Save();


        public double STT
        {
            get { return YoutubeChannelSettingUI.Setting.STT; }
            set { YoutubeChannelSettingUI.Setting.STT = value; NotifyPropertyChange(); Save(); }
        }
        public double GroupName
        {
            get { return YoutubeChannelSettingUI.Setting.GroupName; }
            set { YoutubeChannelSettingUI.Setting.GroupName = value; NotifyPropertyChange(); Save(); }
        }
        public double ChannelInfo
        {
            get { return YoutubeChannelSettingUI.Setting.ChannelInfo; }
            set { YoutubeChannelSettingUI.Setting.ChannelInfo = value; NotifyPropertyChange(); Save(); }
        }
        public double ChannelId
        {
            get { return YoutubeChannelSettingUI.Setting.ChannelId; }
            set { YoutubeChannelSettingUI.Setting.ChannelId = value; NotifyPropertyChange(); Save(); }
        }
        public double Logs
        {
            get { return YoutubeChannelSettingUI.Setting.Logs; }
            set { YoutubeChannelSettingUI.Setting.Logs = value; NotifyPropertyChange(); Save(); }
        }
    }
}
