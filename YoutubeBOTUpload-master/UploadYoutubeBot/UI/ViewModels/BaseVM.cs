using TqkLibrary.WpfUi;
using UploadYoutubeBot.DataClass;

namespace UploadYoutubeBot.UI.ViewModels
{
    internal class BaseVM : BaseViewModel
    {
        protected SettingData Setting { get { return Singleton.Setting.Setting; } }
        protected void SaveSetting() => Singleton.Setting.Save();
        public CopyCommand CopyCommand { get; } = new CopyCommand();
    }
}
